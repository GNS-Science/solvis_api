import pandas as pd

from pathlib import PurePath
import solvis
from api.datastore import model

locs = dict(
    WLG = ["Wellington", -41.276825, 174.777969, 2e5],
    GIS = ["Gisborne", -38.662334, 178.017654, 5e4],
    CHC = ["Christchurch", -43.525650, 172.639847, 3e5],
    IVC = ["Invercargill", -46.413056, 168.3475, 8e4],
    DUD = ["Dunedin", -45.8740984, 170.5035755, 1e5],
    NPE = ["Napier", -39.4902099, 176.917839, 8e4],
    NPL = ["New Plymouth", -39.0579941, 174.0806474, 8e4],
    PMR = ["Palmerston North", -40.356317, 175.6112388, 7e4],
    NSN = ["Nelson", -41.2710849, 173.2836756, 8e4],
    BHE = ["Blenheim", -41.5118691, 173.9545856, 5e4],
    WHK = ["Whakatane", -37.9519223, 176.9945977, 5e4],
    GMN = ["Greymouth", -42.4499469, 171.2079875, 3e4],
    ZQN = ["Queenstown", -45.03, 168.66, 15e3],
    AKL = ["Auckland", -36.848461, 174.763336, 2e6],
    ROT = ["Rotorua", -38.1446, 176.2378, 77e3],
    TUO = ["Taupo", -38.6843, 176.0704, 26e3],
    WRE = ["Whangarei", -35.7275, 174.3166, 55e3],
    LVN = ["Levin", -40.6218, 175.2866, 19e3],
    TMZ = ["Tauranga", -37.6870, 176.1654, 130e3],
    TIU = ['Timaru', -44.3904, 171.2373, 28e3],
    OAM = ["Oamaru", -45.0966, 170.9714, 14e3],
    PUK = ["Pukekohe", -37.2004, 174.9010, 27e3],
    HLZ = ["Hamilton", -37.7826, 175.2528, 165e3],
    LYJ = ["Lower Hutt", -41.2127, 174.8997, 112e3]
)


radii = [10e3,20e3,30e3,40e3,50e3,100e3] #AK could be larger ??

name = "NZSHM22_InversionSolution-QXV0b21hdGlvblRhc2s6NTkzMHJ0YWJU.zip" #60hrs!

#60hr
WORK_PATH = "/home/chrisbc/DEV/GNS/opensha-modular/solvis"

def get_location_radius_rupture_models(solution_id, sol, locations, radii):

    for loc, item in locations.items():
        for radius in radii:
            polygon = solvis.circle_polygon(radius_m=radius, lat=item[1], lon=item[2])
            rupts = set(sol.get_ruptures_intersecting(polygon).tolist())

            print(loc, radius, len(rupts))

            yield model.SolutionLocationRadiusRuptureSet(
                location_radius = f"{loc}:{int(radius)}",
                solution_id = solution_id,
                radius = int(radius),
                location = loc,
                ruptures = rupts,
                rupture_count = len(rupts))


def write():
    model.drop_all()
    model.migrate()

    # d = [x for x in get_location_radius_rupture_models(solution_id, sol, locs, radii)]
    with model.SolutionLocationRadiusRuptureSet.batch_write() as batch:
        for item in get_location_radius_rupture_models(solution_id, sol, locs, radii):
            #print(item)
            #item.save()
            batch.save(item)

def get_ruptures_with_rates(solution_id, sol):
    rs = sol.rupture_sections
    for row in sol.ruptures_with_rates.itertuples():
        sections = [int(x) for x in rs[rs.rupture==int(row[1])].section.tolist()]
        print(sections)
        #row = row.tolist()
        #Pandas(Index=447283, _1=447283, Magnitude=7.010965322902989, _3=-70.0, _4=647095592.8797725, _5=27742.634757962165, _6=5.192883976105789e-05)
        #rupt = dict(rupture_id=row[1], magnitude=row[2], rake=row[3], area=row[4], length=row[5], annual_rate=row[6])
        yield model.SolutionRupture(
            solution_id = solution_id,
            rupture_index = int(row[1]),
            magnitude = float(row[2]),     # Magnitude,
            avg_rake = float(row[3]),     # Average Rake (degrees),
            area_m2 = float(row[4]),       # Area (m^2),
            length_m = float(row[5]),      # Length (m),
            annual_rate = float(row[6]),   # Annual Rate
            fault_sections = sorted(sections)
        )

def write2():
    with model.SolutionRupture.batch_write() as batch:
        for item in get_ruptures_with_rates(solution_id, sol):
            batch.save(item)

def get_fault_sections(solution_id, sol):
    for row in sol.fault_sections.itertuples():
        print(row)
        # Pandas(Index=0, FaultID=0, FaultName='Acton, Subsection 0', DipDeg=60.0, Rake=-70.0, LowDepth=29.0, UpDepth=0.0, DipDir=94.3, AseismicSlipFactor=0.0, CouplingCoeff=1.0, SlipRate=0.2, ParentID=0, ParentName='Acton', SlipRateStdDev=0.15, geometry=<shapely.geometry.linestring.LineString object at 0x7f9a6a529a00>)
        assert 0
        #row = row.tolist()
        # yield model.SolutionFaultSection(
        #     solution_id = solution_id,
        #     rupture_index = int(row[1]),
        #     magnitude = float(row[2]),     # Magnitude,
        #     avg_rake = float(row[3]),     # Average Rake (degrees),
        #     area_m2 = float(row[4]),       # Area (m^2),
        #     length_m = float(row[5]),      # Length (m),
        #     annual_rate = float(row[6]),   # Annual Rate
        #     fault_sections = sorted(sections)
        #     )

def query():

    for item in mSRL.query(f'{solution_id}',
        mSRL.location_radius.startswith("WLG"),
        #filter_condition=mSRL.rupture_count > 200,
        limit=20):
        print("Query returned item {0}".format(item), item.rupture_count)

    for item in mRR.query(f'{solution_id}',
        #mRR.rupture_index == 238707,
        filter_condition=mRR.magnitude > 8,
        limit=20):
        print("Query returned item {0}".format(item), item.magnitude, len(item.fault_sections))

if __name__ == '__main__':

    solution_id = "ZZZ"
    #sol = solvis.InversionSolution().from_archive(PurePath(WORK_PATH,  name))
    #sol = solvis.new_sol(sol, solvis.rupt_ids_above_rate(sol, 0))

    mSRL = model.SolutionLocationRadiusRuptureSet
    mRR = model.SolutionRupture

    model.set_local_mode()

    #get_fault_sections(solution_id, sol)

    # print(sorted(rs[rs.rupture==881].section.tolist()))

    #write()
    #write2()
    #et_ruptures_with_rates(solution_id, sol)
    #assert 0
    query()
    # print()
    # for item in mSRL.scan(limit=20):
    #     print("Query returned item {0}".format(item))

    print('DONE')

# #now export for some science analysis
# df = pd.DataFrame.from_dict(rupture_radius_site_sets, orient='index')
# df = df.rename(columns=dict(zip(radii, [f'r{int(r/1000)}km' for r in radii])))