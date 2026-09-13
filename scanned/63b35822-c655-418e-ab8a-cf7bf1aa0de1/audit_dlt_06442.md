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

```rust
File: lib.rs
184:         #[ink(message, selector = 12)] ## QUERY_STAKED_VALUE_SELECTOR `query_staked_value`
185:         pub fn get_staked_value(&self) -> Balance {
186:             self.staked
187:         }
```

```rust
File: data.rs
155:     pub fn get_weight_imbalances(
156:         &self,
157:         agents: &Vec<Agent>,
158:         total_weight: u64,
159:         total_pooled: u128,
160:     ) -> (u128, u128, u128, Vec<u128>, Vec<i128>) {
..
167:         for a in agents.into_iter() {
168: >>          let staked_amount_current = query_staked_value(a.address) as i128;
..
181:             stakes.push(staked_amount_current as u128);
182:             imbalances.push(diff);
183:         }
184: 
185:         (total_staked, pos_diff, neg_diff, stakes, imbalances)
186:     }
```



Also, when the `staked` value is not synced, and there is a `delegate_unbonding`, at the end this will revert due to unbond more than existing amount bonded, another DOS will happen.

```rust
File: data.rs
278:     pub fn delegate_unbonding(&mut self, azero: Balance) -> Result<(), VaultError> {
..
348:         // Unbond
349:         for (i, a) in agents.iter().enumerate() {
350:             let unbond_amount = unbond_amounts[i];
351:             if unbond_amount > 0 {
352:                 debug_println!("Unbonding {} from agent #{}", unbond_amount, i);
353: >>              if let Err(e) = call_unbond(a.address, unbond_amount) {
354:                     return Err(VaultError::InternalError(e));
355:                 }
356:             }
357:         }
358: 
359:         self.total_pooled = new_total_pooled;
360: 
361:         Ok(())
362:     }
```

**Attack Scenario**

**Attachments**

1. **Proof of Concept (PoC) File**

2. **Revised Code File (Optional)**

**Recommendation**

Since `unbond` operation can be permissionlessly called in a certain situation, when fetching `staked` data, it need to be directly call to the pool for an updated value.
