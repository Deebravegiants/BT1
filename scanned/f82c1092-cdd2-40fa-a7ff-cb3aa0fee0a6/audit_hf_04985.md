# [M] Changes of the UnbondingTime are not accounted

## Summary
Severity: Medium
Contest weight: 0.2608
Dataset id: 22949
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The andromeda-validator-staking contract allows the owner to stake and unstake tokens, adding unstaking entries to an UNSTAKING_QUEUE. The unstaking process is dependent on the UnbondingTime parameter of the chain, which can be changed by governance. If the UnbondingTime is reduced while unstakings are already queued, it can result in a denial-of-service (DoS) situation where newer entries cannot be withdrawn until older entries expire. This could lead to tokens being stuck in the contract for a significant period.
The andromeda-validator-staking contract implements a way to allow the owner of the contract to stake tokens. When the owner of the contract wants to unstake tokens again he can do this by calling the execute_unstake() function. The contract UNSTAKING_QUEUE.
ContractError> {
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
}
Once the completion time has passed, the user can now call execute_withdraw_fund() to withdraw the funds. The function loops over the UNSTAKING_QUEUE and adds all unstakings until it fins one that has not expired. Afterwards all of the found expired unstakings are payed out to the user.
```rust
loop {
    match UNSTAKING_QUEUE.front(deps.storage).unwrap() {
        Some(UnstakingTokens { payout_at, .. }) if payout_at <= env.block.time => {
            if let Some(UnstakingTokens { fund, .. }) = UNSTAKING_QUEUE.pop_front(deps.storage)? {
                funds.push(fund)
            }
        }
        _ => break,
    }
}
```
The completion time that the loop is based upon is the UnbondingTime which is one of the params of the x/staking module. The governance can change this parameter at any time via a MsgUpdateParams message.
The issue occurs as the loop expects that for each item in it itemn:completionTime >= itemn−1:completionTime . Unfortunately this is not the case if the governance reduces the UnbondingTime parameter while unstakings are already queued. In that case it can occur that itemn:completionTime < itemn−1:completionTime. This will result in itemn being unable to withdraw until itemn−1 has expired.
This DOS can be anywhere in the range from 0 − UnbondingTime. For most of the targeted chains the UnbondingTime is set to 21 days (Incetive, Archway and Terra). While it is not a reasonable scenario that the UnbondingTime will be reduced to 0, a deduction of 1-2 weeks is possible. The default value of the UnbondingTime is only 3 days, and some other chains also use 1-2 weeks shorter unbonding times:
• Axelar - 7 days
• Bitcanna - 14 days
• Stargaze - 14 days
Based on this we can assume that a reduction by 1-2 weeks is a possible scenario. As the protocol will not only be deployed on andromeda's own chain but also on multiple other cosmos chains, the Andromeda Governance has no possibility to prevent such a change if it occurs.
The issue results in tokens getting stuck in the contract until the messages before them expire. This can result in a DOS of 1-2 weeks depending on the change of the UnbondingTime.

## Recommendation
We recommend adapting the loop to not break if the payout_at > env.block.time. Instead in that case it should just do nothing and go on to the next element.
```rust
loop {
    match UNSTAKING_QUEUE.front(deps.storage).unwrap() {
        Some(UnstakingTokens { payout_at, .. }) if payout_at <= env.block.time => {
            if let Some(UnstakingTokens { fund, .. }) = UNSTAKING_QUEUE.pop_front(deps.storage)? {
                funds.push(fund)
            }
        }
        _ => continue,
    }
}
```
