# [?] program: fix overflow error in if staking math (#443)

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2023-04-26
Source: https://github.com/velocity-exchange/protocol-v2/commit/84ee075d5454f5920a296479bed91d70f4ad7f39
Type: security-commit

## Details
program: fix overflow error in if staking math (#443)

* bigz/fix-large-insurance-math-error

* update CHANGELOG.md

## Patch
### CHANGELOG.md
```diff
@@ -21,6 +21,8 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 - program: allow amm to pull up to FEE_POOL_TO_REVENUE_POOL_THRESHOLD into fee pool ([#436](https://github.com/drift-labs/protocol-v2/pull/436))
 - program: fix modify order trigger condition
 - sdk: fix removing unstaked sol
+- program: fix math error in settle_revenue_to_insurance_fund for large sizes ([#443](https://github.com/drift-labs/protocol-v2/pull/443))
+
 
 ### Breaking
 
```

### programs/drift/src/controller/insurance.rs
```diff
@@ -11,7 +11,7 @@ use crate::error::ErrorCode;
 use crate::math::amm::calculate_net_user_pnl;
 use crate::math::casting::Cast;
 use crate::math::constants::{
-    MAX_APR_PER_REVENUE_SETTLE_TO_INSURANCE_FUND_VAULT, ONE_YEAR, PERCENTAGE_PRECISION_U64,
+    MAX_APR_PER_REVENUE_SETTLE_TO_INSURANCE_FUND_VAULT, ONE_YEAR, PERCENTAGE_PRECISION,
     SHARE_OF_REVENUE_ALLOCATED_TO_INSURANCE_FUND_VAULT_DENOMINATOR,
     SHARE_OF_REVENUE_ALLOCATED_TO_INSURANCE_FUND_VAULT_NUMERATOR,
 };
@@ -571,15 +571,14 @@ pub fn settle_revenue_to_insurance_fund(
     if spot_market.insurance_fund.user_shares > 0 {
         // only allow MAX_APR_PER_REVENUE_SETTLE_TO_INSURANCE_FUND_VAULT or half revenue pool to be settled
         let capped_apr_amount = insurance_vault_amount
-            .safe_mul(MAX_APR_PER_REVENUE_SETTLE_TO_INSURANCE_FUND_VAULT)?
-            .safe_div(PERCENTAGE_PRECISION_U64)?
+            .cast::<u128>()?
+            .safe_mul(MAX_APR_PER_REVENUE_SETTLE_TO_INSURANCE_FUND_VAULT.cast::<u128>()?)?
+            .safe_div(PERCENTAGE_PRECISION)?
             .safe_div(
                 ONE_YEAR
-                    .cast::<u64>()?
                     .safe_div(spot_market.insurance_fund.revenue_settle_period.cast()?)?
                     .max(1),
-            )?
-            .cast::<u128>()?;
+            )?;
         let capped_token_pct_amount = token_amount.safe_div(10)?;
         token_amount = capped_token_pct_amount.min(capped_apr_amount);
     }
```

### programs/drift/src/controller/insurance/tests.rs
```diff
@@ -1,10 +1,12 @@
 use anchor_lang::prelude::Pubkey;
 
 use crate::controller::insurance::*;
-use crate::math::constants::{QUOTE_PRECISION, SPOT_CUMULATIVE_INTEREST_PRECISION};
+use crate::math::constants::{
+    QUOTE_PRECISION, SPOT_BALANCE_PRECISION, SPOT_CUMULATIVE_INTEREST_PRECISION,
+};
+use crate::state::perp_market::PoolBalance;
 use crate::state::spot_market::InsuranceFund;
 use crate::state::user::UserStats;
-
 #[test]
 pub fn basic_stake_if_test() {
     assert_eq!(0_i32.signum(), 0);
@@ -205,6 +207,145 @@ pub fn basic_seeded_stake_if_test() {
     assert_eq!(if_stake.cost_basis, 1234);
 }
 
+#[test]
+pub fn large_num_seeded_stake_if_test() {
+    let mut if_balance = (199_000_000 * QUOTE_PRECISION) as u64; // ~200M
+    let mut if_stake = InsuranceFundStake::new(Pubkey::default(), 0, 0);
+    let mut user_stats = UserStats {
+        number_of_sub_accounts: 0,
+        ..UserStats::default()
+    };
+    let amount = 199_000_001 as u64; // ~200M + 1
+
+    // all funds in revenue pool
+    let mut spot_market = SpotMarket {
+        deposit_balance: 100 * SPOT_BALANCE_PRECISION,
+        cumulative_deposit_interest: 1111 * SPOT_CUMULATIVE_INTEREST_PRECISION / 1000,
+        insurance_fund: InsuranceFund {
+            unstaking_period: 0,
+            revenue_settle_period: 1,
+            ..InsuranceFund::default()
+        },
+        revenue_pool: PoolBalance {
+            market_index: 0,
+            scaled_balance: 100 * SPOT_BALANCE_PRECISION,
+            ..PoolBalance::default()
+        },
+        ..SpotMarket::default()
+    };
+
+    assert_eq!(spot_market.insurance_fund.total_shares, 0);
+    assert_eq!(spot_market.insurance_fund.user_shares, 0);
+
+    add_insurance_fund_stake(
+        amount,
+        if_balance,
+        &mut if_stake,
+        &mut user_stats,
+        &mut spot_market,
+        0,
+    )
+    .unwrap();
+
+    assert_eq!(spot_market.insurance_fund.total_shares, 199000199000001); // seeded works
+    assert_eq!(spot_market.insurance_fund.user_shares, 199000001);
+    assert_eq!(if_stake.unchecked_if_shares(), amount as u128);
+    if_balance += amount;
+
+    // must request first
+    assert!(remove_insurance_fund_stake(
+        if_balance,
+        &mut if_stake,
+        &mut user_stats,
+        &mut spot_market,
+        0
+    )
+    .is_err());
+    assert_eq!(if_stake.unchecked_if_shares(), amount as u128);
+    let spot_market_vault_amount = get_token_amount(
+        spot_market.deposit_balance,
+        &spot_market,
+        &SpotBalanceType::Deposit,
+    )
+    .unwrap() as u64;
+    assert_eq!(spot_market_vault_amount, 111);
+
+    let flow =
+        settle_revenue_to_insurance_fund(spot_market_vault_amount, if_balance, &mut spot_market, 1)
+            .unwrap();
+    assert_eq!(flow, 11);
+    assert_eq!(spot_market.revenue_pool.scaled_balance, 90099009901);
+    let spot_market_vault_amount = get_token_amount(
+        spot_market.deposit_balance,
+        &spot_market,
+        &SpotBalanceType::Deposit,
+    )
+    .unwrap() as u64;
+    assert_eq!(spot_market_vault_amount, 100);
+
+    if_balance += flow;
+
+    request_remove_insurance_fund_stake(
+        if_stake.unchecked_if_shares(),
+        if_balance,
+        &mut if_stake,
+        &mut user_stats,
+        &mut spot_market,
+        0,
+    )
+    .unwrap();
+    assert_eq!(
+        if_stake.last_withdraw_request_shares,
+        if_stake.unchecked_if_shares()
+    );
+    assert_eq!(if_stake.last_withdraw_request_value, 199000001);
+
+    let amount_returned = (remove_insurance_fund_stake(
+        if_balance,
+        &mut if_stake,
+        &mut user_stats,
+        &mut spot_market,
+        1,
+    ))
+    .unwrap();
+    assert_eq!(amount_returned, amount);
+    if_balance -= amount_returned;
+
+    assert_eq!(if_stake.unchecked_if_shares(), 0);
+    assert_eq!(if_stake.cost_basis, 0);
+    assert_eq!(if_stake.last_withdraw_request_shares, 0);
+    assert_eq!(if_stake.last_withdraw_request_value, 0);
+    assert_eq!(if_balance, 199000000000011);
+    assert_eq!(spot_market.insurance_fund.user_shares, 0);
+    assert_eq!(spot_market.insurance_fund.total_shares, 199000000000000);
+
+    spot_market.revenue_pool.scaled_balance = 100 * SPOT_BALANCE_PRECISION;
+
+    add_insurance_fund_stake(
+        199033744205760,
+        if_balance,
+        &mut if_stake,
+        &mut user_stats,
+        &mut spot_market,
+        20,
+    )
+    .unwrap();
+    assert_eq!(if_stake.cost_basis, 199033744205760);
+    assert_eq!(spot_market.insurance_fund.user_shares, 199033744205748);
+
+    add_insurance_fund_stake(
+        199033744205760,
+        if_balance,
+        &mut if_stake,
+        &mut user_stats,
+        &mut spot_market,
+        30,
+    )
+    .unwrap();
+    assert_eq!(if_stake.cost_basis, 398067488411520);
+    assert_eq!(spot_market.insurance_fund.user_shares, 597134982544960);
+}
+
 #[test]
 pub fn gains_stake_if_test() {
     let mut if_balance = 0;
```
