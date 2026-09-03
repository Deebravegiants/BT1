# [M] Changing a strategy can be bricked

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-sandclock
Published: 2022-01-10
Source: https://github.com/code-423n4/2022-01-sandclock-findings/issues/91
Type: code-finding

## Details
# Handle

kenzo


# Vulnerability details

A vault wouldn't let the strategy be changed unless the strategy holds no funds.
Since anybody can send funds to the strategy, a griefing attack is possible.

## Impact
Strategy couldn't be changed.

## Proof of Concept
`setStrategy` requires `strategy.investedAssets() == 0`. [(Code ref)](https://github.com/code-423n4/2022-01-sandclock/blob/main/sandclock/contracts/Vault.sol#L113:#L116)
`investedAssets` contains the aUST balance and the pending redeems: [(Code ref)](https://github.com/code-423n4/2022-01-sandclock/blob/main/sandclock/contracts/strategy/BaseStrategy.sol#L271)
```
uint256 aUstBalance = _getAUstBalance() + pendingRedeems;
```

So if a griefer sends 1 wei of aUST to the strategy before it is to be replaced, it would not be able to be replaced. The protocol would then need to redeem the aUST and wait for the process to finish - and the griefer can repeat his griefing. As they say, griefers gonna grief.

## Recommended Mitigation Steps
Consider keeping an internal aUST balance of the strategy, which will be updated upon deposit and redeem, and use it (instead of raw aUST balance) to check if the strategy holds no aUST funds.
Another option is to add capability for the strategy to send the aUST to the vault.
