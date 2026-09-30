# [?] apollo_l1_gas_price_config: reject number_of_blocks_for_mean=0 to avoid divide-by-zero panic (#14553) (#14745)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-07-12
Source: https://github.com/starkware-libs/sequencer/commit/ba53156859b5ac403e5aecd2e368fae76b7020d8
Type: security-commit

## Details
apollo_l1_gas_price_config: reject number_of_blocks_for_mean=0 to avoid divide-by-zero panic (#14553) (#14745)

(cherry picked from commit b1cfa5ab86bd08969822ca48be823ba937fd5616)

Co-authored-by: dan-starkware <56217775+dan-starkware@users.noreply.github.com>

## Patch
### crates/apollo_l1_gas_price_config/src/config.rs
```diff
@@ -21,6 +21,10 @@ use starknet_api::core::ChainId;
 use url::Url;
 use validator::Validate;
 
+#[cfg(test)]
+#[path = "config_test.rs"]
+mod config_test;
+
 #[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Validate)]
 pub struct ExchangeRateOracleConfig {
     #[serde(deserialize_with = "deserialize_optional_sensitive_list_with_url_and_headers")]
@@ -93,6 +97,9 @@ impl Default for ExchangeRateOracleConfig {
 #[derive(Clone, Debug, Serialize, Deserialize, Validate, PartialEq)]
 pub struct L1GasPriceProviderConfig {
     // TODO(guyn): these two fields need to go into VersionedConstants.
+    // Must be >= 1: the provider divides the summed prices by this window when computing the mean,
+    // so a value of 0 would cause a divide-by-zero panic during block production.
+    #[validate(range(min = 1))]
     pub number_of_blocks_for_mean: u64,
     // Use seconds not Duration since seconds is the basic quanta of time for both Starknet and
     // Ethereum.
```

### crates/apollo_l1_gas_price_config/src/config_test.rs
```diff
@@ -0,0 +1,16 @@
+use validator::Validate;
+
+use super::L1GasPriceProviderConfig;
+
+// A zero mean window would make the provider divide by zero when computing the mean gas price,
+// so it must be rejected at config load instead of panicking later during block production.
+#[test]
+fn rejects_zero_number_of_blocks_for_mean() {
+    let config = L1GasPriceProviderConfig { number_of_blocks_for_mean: 0, ..Default::default() };
+    assert!(config.validate().is_err());
+}
+
+#[test]
+fn accepts_default_number_of_blocks_for_mean() {
+    assert!(L1GasPriceProviderConfig::default().validate().is_ok());
+}
```
