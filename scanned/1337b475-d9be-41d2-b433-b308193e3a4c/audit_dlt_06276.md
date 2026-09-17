# [M] `stop_farm()` doesn't check whether the farm is already stopped

## Summary
Severity: Medium
Chain: Smart contract
Component: AlephZeroAMM
Published: 2024-01-22
Source: https://github.com/hats-finance/AlephZeroAMM-0x0d88a9ece90994ecb3ba704730819d71c139f60f/issues/32
Type: hats-finding

## Details
**Github username:** @rodiontr
**Twitter username:** --
**Submission hash (on-chain):** 0xbc19b6d6ebf43aff12005a90acea5ee63b8afcb08f6bec9ac855f6f1061679b1
**Severity:** medium

**Description:**
**Description**\

`stop_farm` function allows the owner to stop the farming at any given moment. It makes `end` of the farm to be set to the current `block.timestamp`. The problem is that, due to improper input validation, the `stop_farm()` can be called repeatedly and the farm `end` can be repeatedly updated meaning that the farm is not actually stopped by using this function. This also makes the params that set in the `owner_start_new_farm` being senseless as they can be changed at any given moment.


**Attack Scenario**\

Let's say the `end` is set to the current `block.timestamp`. So the owner calls `stop_farm` and this happens:

```
fn owner_stop_farm(&mut self) -> Result<(), FarmError> {
            ensure!(self.env().caller() == self.owner, FarmError::CallerNotOwner);
            self.update()?;
            self.end = self.env().block_timestamp();
            Ok(())
        }
```

Now, 2 days later, the owner can call this func again, and, due to insufficient validation, he can do it and `end` timestamp is updated to the current `block_timestamp` meaning the farm is active again. This could cause different inconveniences in the future if there'd be the checks for the farm being active.


**Recommendation**

Make sure that the `stop_farm` eventually stops the farm and it could not be redeployed again with the new `block_timestamp`:

```diff

+ensure!(is_stopped(), FarmError::AlreadyStopped)

```
