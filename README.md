# 한국 팩터 모델 v2 (Fama-French 3-Factor)

## 개요

이 프로젝트는 Fama-French(1993) 3 팩터 모델을 한국 시장에 맞게 전면 재구축한 것입니다. **KOSPI + KOSDAQ 1,284개 종목**을 대상으로 **2000년~2026년** 기간의 가치加重(VW) 수익률과 한국종합채권Monkey 금리 기반 무위험수익률을 사용합니다.

## v1 대비 주요 변경사항
| 구분 | v1 | v2 |
|------|-----|-----|
| **분석종목** | KOSPI Mainly (~247종) | **KOSPI + KOSDAQ (1,284종)** |
| **기간** | 2007-07 ~ 2026-05 | **2000-07 ~ 2026-05** (+84개월) |
| **무위험수익률** | M000911034 (DCF 금리) | **한국종합채권Monkey 금리** |
| **가중방식** | 단일가중(EW) | **가치加重(VW)** |
| **팩터** | 포함 | **제외** |
| **금융업** | 포함 | **명칭 기반 제외** |

## 데이터 소스

- **종목 수익률**: FnGuide 결합 문서1.xlsx (1,284개 종목, 2000-2026)
- **무위험수익률**: 한국종합채권Monkey 금리 (자동 CSV)
- **미국 비교**: Ken French Data Library (1963-1991)

## 방법론
### 수익률 계산
- **가격수익률만 사용**: 보통주 우선(S410000700) 기말方式进行 총수익률 대신 **현금배당 미포함**
- 기간수익률: `R_t = (P_t - P_{t-1}) / P_{t-1}`

### 포트폴리오 구성 (Fama-French 1993 방법)
- **규모 분류**: 6포트리오별 총액 중위값으로 구분(Small / Big)
- **BM 분류**: 직전 연도 12월 말가액/ 직전 6개월 총액 기준 30/70 백분위(L/M/H)
- **보유기간**: 7월t ~ 6월t+1
- **가중**: 총액 가중(lagged ME 사용)

### 팩터
- **우선권제외**: 코드 앞자리 5/6/7
- **금융업제외**: 명칭 패턴 (우선/증권/보험/카드/캐피탈/신규금융/신탁/손해보험/생명보험)
- **결측치 처리**: 결산일 기준 BM에 NaN으로 설정 (제외시점 다음)

## 한계점
1. **배당 미포함**: 가격수익률만 사용으로 총수익률 아님
2. ** survivor bias**: FnGuide 데이터에 survivo bias 존재 가능
3. **금융업명칭 패턴**: 사업코드 앞 문자 명칭 패턴으로 제외
4. **기간 불일치**: 미국(1963-1991) vs 한국(2000-2026) 경기환경 차이
5. **BOK 무위험수익률 근사**: 기간 선물 금리에서 기간 무위危険 수익률 추출

## 팩터 통계 (2000-07 ~ 2026-05)

| 팩터 | 평균 | 표준편차 | t-통계량 |
|------|------|----------|----------|
| Mkt-RF | 0.714% | 6.64% | 1.90 |
| SMB | -0.674% | 4.63% | -2.57 |
| HML | 0.826% | 3.74% | 3.89 |

## v1 vs v2 상관관계 (2007-07 ~ 2026-05 중첩기간)

| 팩터 | 상관관계 |
|------|----------|
| Mkt-RF | 0.997 |
| SMB | 0.952 |
| HML | 0.791 |

> **HML 상관관계 0.791 의미**: KOSDAQ 포함 + 가치加重(VW) 방식으로 인해 v1(단일가중 KOSPI only)과 차이 발생. 이는 방법론적 차이에 의한 결과이며, v2가 보다 전면적이고 정확한 현실을 반영합니다.

## 프로젝트 구조

```
.
├── data/
│   ├── convert_rf.py              # 무위험수익률 변환 스크립트
│   ├── book_equity_monthly.parquet # 월별 명目가액 데이터
│   ├── financial_data_long.parquet # 재무 데이터(long format)
│   ├── market_data_long.parquet    # 시장 데이터(long format)
│   ├── market_excess_return.parquet # 시장 초과수익률 데이터
│   ├── panel_data.parquet          # 결합 패널 (수익률, 시총, BM)
│   └── stock_returns.parquet       # 개별종목 월간수익률 데이터
├── output/
│   ├── charts/
│   │   ├── cumulative_returns.png          # 누적수익차트
│   │   ├── factor_premium_comparison.png     # 팩터 프리미엄 비교
│   │   └── heatmap_25.png                    # 25포트폴리오 히트맵
├── scripts/
│   ├── convert_excel_to_parquet.py # Excel to Parquet 변환
│   ├── calc_stock_returns.py       # 개별종목 수익률계산
│   ├── construct_6_portfolios.py   # 6 포트폴리오구성
│   ├── build_25_portfolios.py       # 25 포트폴리오구성
│   ├── run_regression_korea.py     # FF3 회귀분석
│   ├── load_us_data.py             # 미국 데이터로드
│   └── verify_parquet.py           # Parquet 검증스크립트
├── tests/
│   └── test_outputs.py             # 21개 패턴 기반 테스트 suite
├── build_panel_data.py             # 패널 데이터구축
├── qa_check.py                     # QA 검증체크립트
├── config.py                       # 프로젝트 설정
├── requirements.txt                # 의존성 패키지
├── run.sh                          # 전체 실행 스크립트
└── README.md                       # 본 문서
```

## 실행 방법

```bash
# 전체 분석 일괄 실행
bash run.sh

# 또는 개별 스크립트 실행
python scripts/convert_excel_to_parquet.py
python scripts/calc_stock_returns.py
python build_panel_data.py
python scripts/construct_6_portfolios.py
python scripts/build_25_portfolios.py
python scripts/run_regression_korea.py
```

## 테스트
```bash
python -m pytest tests/ -v
```

모든 테스트는 **패턴 기반**으로 작성되어 하드코딩된 기댓값을 사용하지 않습니다.

## 참고문헌

- Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3-56.

---

*이 프로젝트는 OhMyOpenCode Sisyphus 도움으로 구축되었습니다.*