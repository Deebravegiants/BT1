# [H] stale price can be prolonged

## Summary
Severity: High
Chain: Smart contract
Component: Common--Stableswap
Published: 2024-07-21
Source: https://github.com/hats-finance/Common--Stableswap-0xd4d9a2772202ce33b24901d3fc94e95a84b37430/issues/27
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xa5ff0025f883e6ad8db3fb5bb463cc4d509acd300df8762751c005782eb68a98
**Severity:** high

**Description:**
### Description
 `force_update_rate` allows for any user to forcefully update a price rate:
```javascript
    /// Update rate without expiry check.
    ///
    /// Returns `true` if value of the new rate is different than the previous.
    pub fn force_update_rate(&mut self, current_time: u64) -> bool {
        match self {
            Self::External(external) => external.update_rate_no_cache(current_time),
            Self::Constant(_) => false,
        }
    }
}
```
inside the flow of this execution, fn `update` is called:
```javascript
 fn update(&mut self, current_time: u64) -> bool {
        let old_rate = self.cached_token_rate;
        self.cached_token_rate = Self::query_rate(self.token_rate_contract);
->        self.last_token_rate_update_ts = current_time;
        old_rate != self.cached_token_rate
    }
```
`last_token_rate_update_ts` is updated to the `current_time` regardless of whether the price has changed since the last update. If the price hasn't changed, the function will return false, but `last_token_rate_update_ts` will still be successfully updated.

This is problematic, it can lead to the following scenario:

Bob is the malicious user in this example:

- Token A's Oracle becomes `stale` (this can happen due to several reasons)
- Bob keeps on calling `force_update_rate` as long as Token A is `stale`
- for the sake of the example the `expiration_duration_ms` is set to 12 hours
- Token A's  oracle returns `unstale`
- Bob calls `swap_exact_in`
```javascript
            // Make sure rates are up to date before we attempt any calculations
->            self.update_rates();
            let rates = self.get_scaled_rates(&self.pool.token_rates)?;
```
Inside the function, a check is performed to see if the rates are outdated. They will not be considered outdated since Bob kept calling `force_update_rate` to repeatedly reset the expiration timer. 

- Bob can now profit by executing the swap using the stale price.

This means that for approximately `expiration_duration_ms` after the price becomes `unstale`, the stale price will still be retrieved when calling `swap_exact_in`.

Note that this does not require a malicious user to have effect on the protocol. A honest user can also unknowingly suffer from this.

### Recommendation
Implement logic to prevent the exploitation of stale prices. For example, whenever a user calls `force_update_rate` you could avoid updating the `last_token_rate_update_ts` when the price has not changed.
