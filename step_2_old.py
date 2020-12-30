import csv
import os
from datetime import datetime, timezone, timedelta
from math import floor


# from step_1 import ComplexDetails
def main():
    print("동별 가격 분석을 시작합니다..")
    files = os.listdir("./")
    files = [file for file in files if file.endswith('csv')]
    if len(files) == 0:
        print("분석할 데이터 파일이 없습니다.")
        return
    prices_by_towns = {}
    towns = []

    high_price = 0
    low_price = 9999999999999999999
    print("분석할 데이터 파일 리스트를 확인하세요.")
    for file in files:
        print(file)
    ok = str(input("진행할까요?( y or n ) : ")).lower()
    while True:
        if ok == 'y':
            break
        elif ok == 'n':
            return
        else:
            print("잘못 입력하였습니다. 'y' 나 'n'만 이력하세요! :")

    for file in files:
        try:
            town = file[15:-4]
            towns.append(town)
            prices_by_towns[town] = []
            with open(file, 'r', encoding='utf-8-sig', newline='') as f:
                rows = csv.reader(f, delimiter=',')
                next(rows)  # skip header
                row_no = 1
                for row in rows:
                    if row[22].lower() == "v":
                        trade_price = int(row[8]) if row[8] else None
                        if trade_price and trade_price > high_price:
                            high_price = trade_price
                        elif trade_price and trade_price < low_price:
                            low_price = trade_price

                        if trade_price:
                            name = row[0]
                            pyeong = row[4]
                            price = float(trade_price / 10000)
                            prices_by_towns[town].append({
                                'name': name,
                                'pyeong': pyeong,
                                'price': price
                            })
                    row_no += 1
        except Exception as e:
            print("잘못된 파일입니다. 확인해주세요.")
            print("파일명 :", file)
            print("오류행 :", row_no)
            print("오류내용 :", e)
            return

    try:
        gap = float(floor((high_price - low_price) / 90000))
        start_price = float(floor(low_price / 10000))
        result = []
        for i in range(10):
            result.append(
                {'period': (start_price, start_price + gap),
                 'complexes': {t: [] for t in towns}
                 }
            )
            start_price += gap

        result.reverse()

        for t in prices_by_towns.keys():
            for d in prices_by_towns[t]:
                for r in result:
                    low, high = r.get('period')
                    if low <= d.get('price') < high:
                        r.get('complexes').get(t).append(f"{d.get('name')}({d.get('pyeong')}평/{d.get('price')})")

        created_time = datetime.now(timezone(timedelta(hours=9)))
        file_name = f"({created_time.strftime('%y%m%d_%H%M%S')})동별가격"
        with open(f'./{file_name}.csv', 'w', encoding='utf-8-sig', newline='') as f:
            wt = csv.writer(f)
            wt.writerow(['전체'] + towns)
            for r in result:
                complexes = r.get('complexes')
                row = [f"{r.get('period')[0]} ~ {r.get('period')[1]}"]
                for t in towns:
                    c = ""
                    for complex in complexes.get(t):
                        c += (complex + "\r")
                    row.append(f"{c}")
                wt.writerow(
                    row
                )
        print("동별 가격 분석을 완료하였습니다!")
    except Exception as e:
        print("오류가 발생하였습니다.")
        print(e)
        return


main()
