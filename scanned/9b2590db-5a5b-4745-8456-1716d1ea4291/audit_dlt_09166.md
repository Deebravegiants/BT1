# [?] runtime: Prevent panic if gas limit is too large

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2022-01-07
Source: https://github.com/graphprotocol/graph-node/commit/c51fe3604e793febaf127408675d209fc31b5c4e
Type: security-commit

## Details
runtime: Prevent panic if gas limit is too large

## Patch
### graph/src/runtime/gas/costs.rs
```diff
@@ -13,7 +13,7 @@ const GAS_PER_SECOND: u64 = 10_000_000_000;
 /// like 10 gas for ~1ns allows us to be granular in instructions which are aggregated into metered
 /// blocks via https://docs.rs/pwasm-utils/0.16.0/pwasm_utils/fn.inject_gas_counter.html But we can
 /// still charge very high numbers for other things.
-const CONST_MAX_GAS_PER_HANDLER: u64 = 1000 * GAS_PER_SECOND;
+pub const CONST_MAX_GAS_PER_HANDLER: u64 = 1000 * GAS_PER_SECOND;
 
 lazy_static! {
     /// This is configurable only for debugging purposes. This value is set by the protocol,
```

### runtime/wasm/src/gas_rules.rs
```diff
@@ -1,6 +1,6 @@
 use std::{convert::TryInto, num::NonZeroU32};
 
-use graph::runtime::gas::MAX_GAS_PER_HANDLER;
+use graph::runtime::gas::CONST_MAX_GAS_PER_HANDLER;
 use parity_wasm::elements::Instruction;
 use pwasm_utils::rules::{MemoryGrowCost, Rules};
 
@@ -158,7 +158,7 @@ impl Rules for GasRules {
         // free pages because this is 32bit WASM.
         const MAX_PAGES: u64 = 12 * GIB / PAGE;
         let gas_per_page =
-            NonZeroU32::new((*MAX_GAS_PER_HANDLER / MAX_PAGES).try_into().unwrap()).unwrap();
+            NonZeroU32::new((CONST_MAX_GAS_PER_HANDLER / MAX_PAGES).try_into().unwrap()).unwrap();
 
         Some(MemoryGrowCost::Linear(gas_per_page))
     }
```
