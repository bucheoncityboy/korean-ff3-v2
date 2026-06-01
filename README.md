# 한국 팩터 모델 v2 (Fama-French 3-Factor)

## 개요

본 프로젝트는 Fama-French(1993) 3팩터 모델을 한국 시장에 맞게 전면 재구축한 것입니다. **KOSPI + KOSDAQ 1,284개 종목**을 대상으로 **2000년~2026년** 기간의 가치가중(VW) 포트폴리오 수익률과 한국은행 기준금리를 무위험수익률로 사용합니다.

## v1 대비 주요 변경사항

| 항목 | v1 | v2 |
|------|-----|-----|
| **대상 종목** | KOSPI 제조업 (~247개) | **KOSPI + KOSDAQ (1,054개)** |
| **기간** | 2007-07 ~ 2026-05 | **2000-07 ~ 2026-05** (+84개월) |
| **무위험수익률** | M000911034 (DCF 금리) | **한국은행 기준금리** |
| **가중방식** | 동일가중 (EW) | **가치가중 (VW)** |
| **우선주** | 포함 | **제외** |
| **금융주** | 포함 | **명칭 기반 제외** |

## 데이터 소스

- **종목 데이터**: FnGuide 통합 문서1.xlsx (1,284개 종목, 2000-2026)
- **무위험수익률**: 한국은행 기준금리 (수동 CSV)
- **미국 비교**: Ken French Data Library (1963-1991)

## 방법론

### 수익률
- **가격수익률만 사용**: 수정주가(S410000700) 기준으로 스톡스플릿은 반영되나 **현금배당은 미포함**
- 월간수익률: `R_t = (P_t - P_{t-1}) / P_{t-1}`

### 포트폴리오 구성 (Fama-French 1993 표준)
- **규모 분류**: 6월 시가총액 중위수 → 소형(Small) / 대형(Big)
- **BM 분류**: 전년 12월 장부가치 / 6월 시가총액 → 30/70 백분위 (L/M/H)
- **보유기간**: 7월 t ~ 6월 t+1
- **가중**: 시가총액 가중 (lagged ME 사용)

### 필터
- **우선주 제외**: 코드 끝자리 5/6/7
- **금융주 제외**: 명칭 패턴 (은행/증권/보험/카드/캐피탈/저축/금융/신탁/손해보험/생명보험)
- **음수 장부가치**: 플래그 처리 후 BM을 NaN으로 설정 (제외하지 않음)

## 한계점

1. **배당 미포함**: 가격수익률만 사용하여 총수익률이 아님
2. **생존편향**: FnGuide 데이터에 생존편향 존재 가능
3. **금융주 명칭 필터링**: 산업코드 없이 명칭 패턴으로 제외
4. **기간 불일치**: 미국(1963-1991) vs 한국(2000-2026) — 경제 환경 상이
5. **BOK 무위험수익률 근사**: 연간 기준금리에서 월간 무위험수익률 도출

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

> **HML 상관관계 0.791 설명**: KOSDAQ 포함 및 가치가중(VW) 방식으로 인해 v1(동일가중, KOSPI만)과 차이 발생. 이는 방법론적 차이의 예상된 결과이며, v2가 더 완전한 시장 표현임.

## 프로젝트 구조

```
.
├── data/
│   ├── convert_rf.py              # 무위험수익률 변환
│   ├── book_equity_monthly.parquet # 월별 장부가치
│   ├── financial_data_long.parquet # 재무 데이터 (long format)
│   ├── market_data_long.parquet   # 시장 데이터 (long format)
│   ├── market_excess_return.parquet # 시장 초과수익률
│   ├── panel_data.parquet         # 통합 패널 (수익률, 시총, 장부가치, BM)
│   └── stock_returns.parquet      # 개별종목 월간수익률
├── output/
│   ├── charts/
│   │   ├── cumulative_returns.png          # 누적수익률 차트
│   │   ├── factor_premium_comparison.png     # 팩터 프리미엄 비교
│   │   └── heatmap_25.png                    # 25포트폴리오 히트맵
│   └── compute_comparison.py      # v1-vs-v2 비교 분석
├── scripts/
│   ├── convert_excel_to_parquet.py # Excel → Parquet 변환
│   ├── calc_stock_returns.py       # 개별종목 수익률 계산
│   ├── construct_6_portfolios.py   # 6 포트폴리오 구성
│   ├── build_25_portfolios.py      # 25 포트폴리오 구성
│   ├── run_regression_korea.py     # FF3 회귀분석
│   ├── load_us_data.py             # 미국 데이터 로드
│   └── verify_parquet.py           # Parquet 검증
├── tests/
│   └── test_outputs.py             # 21개 패턴 기반 테스트
├── build_panel_data.py             # 패널 데이터 구축
├── qa_check.py                     # QA 검증 스크립트
├── config.py                       # 프로젝트 설정
├── requirements.txt                # 의존성
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
python output/compute_comparison.py
```

## 테스트

```bash
python -m pytest tests/ -v
```

모든 테스트는 **패턴 기반**으로 작성되어 하드코딩된 기댓값을 사용하지 않습니다.

## 참고문헌

- Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3-56.

---

*본 프로젝트는 OhMyOpenCode Sisyphus 에이전트를 통해 구축되었습니다.*
