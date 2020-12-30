import csv
import os
from datetime import datetime, timezone, timedelta
from math import floor


# from step_1 import ComplexDetails
def main():
    print("동별 가격 분석을 시작합니다..")
    files = os.listdir("./")
    files = [file for file in files if file.endswith('csv') and not file.startswith('_')]
    if len(files) == 0:
        print("분석할 데이터 파일이 없습니다.")
        return
    prices_by_towns = {}
    towns = []

    high_price = 0
    low_price = 9999999999999999999
    selected_files = []
    print("분석할 데이터 파일 리스트를 확인하세요.")
    while True:
        for no, file in enumerate(files):
            print(no+1, file, '--', no+1)
        print("분석할 파일번호를 선택하세요.(전체선택: 0, 종료: q)")
        ok = str(input("(예: 1번 2번 파일만 분석하고 싶다면: 1 2 입력): ")).lower()
        if ok == 'q':
            return
        nos = ok.split(sep=' ')
        if ok == '0':
            break
        try:
            for no in nos:
                selected_files.append(files[int(no) - 1])
            files = selected_files
        except Exception as e:
            print("잘못입력하였습니다.")
            continue
        break

    print()

    while True:
        try:
            analysis_pyeong = int(input("분석할 평형을 입력 하세요.(10, 20, 30, 40, 50, 60, 70, 80):"))
            if analysis_pyeong not in (10, 20, 30, 40, 50, 60, 70, 80):
                print("올바른 평형을 입력하세요.")
                continue
            break
        except Exception as e:
            print("잘못입력하였습니다.다시 입력하세요.")
            print("오류내용:", e)
            continue

    while True:
        try:
            latest_year = int(input("신축 기준 년도를 입력하세요(년도 4자리 숫):"))
            sub_latest_year = int(input("준 신축 기준 년도를 입력하세요(년도 4자리 숫자):"))
            if latest_year < 1900 or sub_latest_year < 1900:
                print("1900년도 이전에 지어진 아파트는 없을테죠?")
                continue
            elif latest_year > datetime.today().year or sub_latest_year > datetime.today().year:
                print("미래년도를 기준으로 잡을 수 없습니다.")
                continue
            elif sub_latest_year >= latest_year:
                print("구축년도 기준이 신축년도 기준보다 작아야 합니다.")
                continue
            break
        except Exception as e:
            print("올바를 년도 형식을 입력하세요.(예: 2020)")
            print("오류내용:", e)
            continue

    for file in files:
        try:
            town = file[15:-4]
            towns.append(town)
            prices_by_towns[(town, 'old')] = []
            prices_by_towns[(town, 'sub_latest')] = []
            prices_by_towns[(town, 'latest')] = []
            with open(file, 'r', encoding='utf-8-sig', newline='') as f:
                rows = csv.reader(f, delimiter=',')
                next(rows)  # skip header
                row_no = 1
                for row in rows:
                    if len(row) <= 1:
                        continue
                    is_representative = row[22].lower()
                    pyeong = int(row[4]) if row[4] else 0
                    if is_representative == "v" and (analysis_pyeong <= pyeong < analysis_pyeong + 10):
                        trade_price = int(row[8]) if row[8] else None
                        if trade_price and trade_price > high_price:
                            high_price = trade_price
                        elif trade_price and trade_price < low_price:
                            low_price = trade_price

                        if trade_price:
                            name = row[0]
                            pyeong = row[4]
                            price = float(trade_price / 10000)
                            approved_year = int(row[1].replace("'", "").strip()[:4])
                            if approved_year >= latest_year:
                                key = (town, "latest")
                            elif approved_year >= sub_latest_year:
                                key = (town, "sub_latest")
                            else:
                                key = (town, "old")
                            prices_by_towns[key].append({
                                'name': name,
                                'pyeong': pyeong,
                                'price': price,
                                'approved_year': approved_year
                            })
                    row_no += 1
        except Exception as e:
            print("잘못된 파일입니다. 확인해주세요.")
            print("파일명 :", file)
            print("오류행 :", row_no)
            print("오류내용 :", e)
            return

    try:
        gap = float(round((high_price - low_price) / 90000, 1))
        start_price = float(floor(low_price / 10000))
        print(f"최고가: {high_price}")
        print(f"최저가: {low_price}")
        print(f"구간간격: {gap}")
        result = []
        for i in range(10):
            result.append(
                {'period': (start_price, round(start_price + gap, 1)),
                 'complexes': {key: [] for key in prices_by_towns.keys()}
                 }
            )
            start_price = round(start_price + gap, 1)

        result.reverse()

        for key, items in prices_by_towns.items():
            for d in items:
                for r in result:
                    low, high = r.get('period')
                    if low <= d.get('price') < high:
                        r.get('complexes').get(key).append(f"{d.get('name')}({d.get('pyeong')}평/{d.get('price')}/{str(d.get('approved_year'))[2:]}년)")
        created_time = datetime.now(timezone(timedelta(hours=9)))
        file_name = f"_({created_time.strftime('%y%m%d_%H%M%S')})_{analysis_pyeong}평_동별가격_분석"
        with open(f'./{file_name}.csv', 'w', encoding='utf-8-sig', newline='') as f:
            wt = csv.writer(f)
            headers = []
            wt.writerow(['동네'] + [key[0] for key in prices_by_towns.keys()])
            for key in prices_by_towns.keys():
                if key[1] == 'old':
                    headers.append(f"구축(~{sub_latest_year})")
                elif key[1] == 'sub_latest':
                    headers.append(f"준신축({sub_latest_year}~{latest_year})")
                elif key[1] == 'latest':
                    headers.append(f"신축({latest_year}~)")
            wt.writerow(['시기'] + headers)
            for r in result:
                complexes = r.get('complexes')
                row = [f"{r.get('period')[0]} ~ {r.get('period')[1]}"]
                for key in prices_by_towns.keys():
                    c = ""
                    for cx in complexes.get(key):
                        c = c + "\n" if len(c) > 0 else c
                        c += cx
                    row.append(f"{c}")
                wt.writerow(
                    row
                )
        print("동별 가격 분석을 완료하였습니다!")
    except Exception as e:
        print("오류가 발생하였습니다.")
        raise(e)
        return


main()
