# [M] Changes of the `UnbondingTime` are not accounted for

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-05-andromeda-ado
Published: 2024-06-23
Source: https://github.com/sherlock-audit/2024-05-andromeda-ado-judging/issues/54
Type: sherlock-finding

## Details
J4X_

Medium

# Changes of the `UnbondingTime` are not accounted for

## Summary

The `andromeda-validator-staking` contract allows the owner to stake and unstake tokens, adding unstaking entries to an `UNSTAKING_QUEUE`. The unstaking process is dependent on the `UnbondingTime` parameter of the chain, which can be changed by governance. If the `UnbondingTime` is reduced while unstakings are already queued, it can result in a denial-of-service (DoS) situation where newer entries cannot be withdrawn until older entries expire. This could lead to tokens being stuck in the contract for a significant period.

## Vulnerability Detail

The `andromeda-validator-staking` contract implements a way to allow the owner of the contract to stake tokens. When the owner of the contract wants to unstake tokens again he can do this by calling the `execute_unstake()` function. The contract will then, on response from the staking module, add an entry to the `UNSTAKING_QUEUE`. 

```rust
pub fn on_validator_unstake(deps: DepsMut, msg: Reply) -> Result<Response, ContractError> {
    let attributes = &msg.result.unwrap().events[0].attributes;
    let mut fund = Coin::default();
    let mut payout_at = Timestamp::default();
    for attr in attributes {
        if attr.key == "amount" {
            fund = Coin::from_str(&attr.value).unwrap();
        } else if attr.key == "completion_time" {
            let completion_time = DateTime::parse_from_rfc3339(&attr.value).unwrap();
            let seconds = completion_time.timestamp() as u64;
            let nanos = completion_time.timestamp_subsec_nanos() as u64;
            payout_at = Timestamp::from_seconds(seconds);
            payout_at = payout_at.plus_nanos(nanos);
        }
    }
    UNSTAKING_QUEUE.push_back(deps.storage, &UnstakingTokens { fund, payout_at })?;

    Ok(Response::default())
}
```

Once the completion time has passed, the user can now call `execute_withdraw_fund()` to withdraw the funds. The function loops over the `UNSTAKING_QUEUE` and adds all unstakings until it fins one that has not expired. Afterwards all of the found expired unstakings are payed out to the user.


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2024-05-andromeda-ado-judging/issues/54_
