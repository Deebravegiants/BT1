# [?] fix: arbitrum nitro gas estimation overflows (#4947)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2024-12-05
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/4cb2c9ae416f08aff55e0abc09bfddf1f83c6513
Type: security-commit

## Details
fix: arbitrum nitro gas estimation overflows (#4947)

### Description

The originally set balance when estimating arbitrum nitro gas was
causing RPC errors, which @tkporter pointed out could be due to an
overflow in the node's code. This PR sets the balance to 100 ETH, which
does fix the error

### Drive-by changes

<!--
Are there any minor or drive-by changes also included?
-->

### Related issues

<!--
- Fixes #[issue number here]
-->

### Backward compatibility

<!--
Are these changes backward compatible? Are there any infrastructure
implications, e.g. changes that would prohibit deploying older commits
using this infra tooling?

Yes/No
-->

### Testing

<!--
What kind of testing have these changes undergone?

None/Manual/Unit Tests
-->

## Patch
### rust/main/chains/hyperlane-ethereum/src/contracts/mailbox.rs
```diff
@@ -2,7 +2,7 @@
 #![allow(missing_docs)]
 
 use std::collections::HashMap;
-use std::ops::RangeInclusive;
+use std::ops::{Mul, RangeInclusive};
 use std::sync::Arc;
 
 use async_trait::async_trait;
@@ -11,6 +11,7 @@ use ethers::abi::{AbiEncode, Detokenize};
 use ethers::prelude::Middleware;
 use ethers_contract::builders::ContractCall;
 use ethers_contract::{Multicall, MulticallResult};
+use ethers_core::utils::WEI_IN_ETHER;
 use futures_util::future::join_all;
 use hyperlane_core::rpc_clients::call_and_retry_indefinitely;
 use hyperlane_core::{BatchResult, QueueOperation, ReorgPeriod, H512};
@@ -560,8 +561,8 @@ where
                 arbitrum_node_interface
                     .estimate_retryable_ticket(
                         H160::zero().into(),
-                        // Give the sender a deposit, otherwise it reverts
-                        U256::MAX.into(),
+                        // Give the sender a deposit (100 ETH), otherwise it reverts
+                        WEI_IN_ETHER.mul(100u32),
                         self.contract.address(),
                         U256::zero().into(),
                         H160::zero().into(),
```
