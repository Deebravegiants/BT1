# [M] unsynced `staked` value when unbond open for DOS

## Summary
Severity: Medium
Chain: Smart contract
Component: Kintsu
Published: 2024-05-25
Source: https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/issues/63
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x2d23de0c9d7156034066433cc1df3172c24047206c11edb578419542588dd525
**Severity:** medium

**Description:**
**Description**\

Unbounding process will be triggered via this `start_unboud` function below:

```rust
File: lib.rs
083:         pub fn start_unbond(&mut self, amount: u128) -> Result<(), RuntimeError> {
084:             // Restricted to vault
085:             if Self::env().caller() != self.vault {
086:                 return Err(RuntimeError::Unauthorized);
087:             }
088: 
089: >>          self.staked -= amount;
090: 
091:             // Trigger un-bonding process
092:             self.env()
093:                 .call_runtime(&RuntimeCall::NominationPools(
094:                     NominationCall::Unbond {
095:                         member_account: MultiAddress::Id(Self::env().account_id()),
096:                         unbonding_points: amount,
097:                     }
098:                 ))?;
099: 
100:             Ok(())
101:         }
```

The issue here is `staked` value will be unsynced due to the unbond can be permissionlessly called by anyone when [`the pool is destroying and the member is not the depositor`](https://github.com/paritytech/polkadot-sdk/blob/master/substrate/frame/nomination-pools/src/lib.rs#L2095-L2097).

Thus when someone trigger this `unbond` operation for a pool, this `staked` value is not updated.

This `staked` var is fetched via `get_staked_value` then it finally called in `get_weight_imbalances`. Using outdated `staked` value, this can affect `delegate_unbonding` allocation.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/issues/63_
