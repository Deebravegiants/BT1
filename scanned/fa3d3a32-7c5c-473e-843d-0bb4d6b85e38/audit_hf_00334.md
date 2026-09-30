# [M] [WP-H7] `InsuranceFund#syncDeps`

## Summary
Severity: Medium
Contest weight: 0.5604
Dataset id: 1628
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function syncDeps(IRegistry _registry) public onlyGovernance {
    vusd = IERC20(_registry.vusd());
    marginAccount = _registry.marginAccount();
}
```

The `Governance` address can call `InsuranceFund.sol#syncDeps()` to change the contract address of `vusd` anytime.

However, since the tx to set a new address for `vusd` can get in between users’ txs to deposit and withdraw, in some edge cases, it can result in users’ loss of funds.

## Proof of Concept
1. Alice deposited `1,000,000 VUSD` to `InsuranceFund`;
2. Gov called `syncDeps()` and set `vusd` to the address of `VUSDv2`;
3. Alice called `withdraw()` with all the `shares` and get back `0 VUSDv2`.

As a result, Alice suffered a fund loss of `1,000,000 VUSD`.

## Recommendation
1. Consider making `vusd` unchangeable;
2. If a possible migration of `vusd` must be considered, consider changing the `syncDeps()` to:

```solidity
function syncDeps(IRegistry _registry) public onlyGovernance {
    uint _balance = balance();
    vusd = IERC20(_registry.vusd());
    require(balance() >= _balance);
    marginAccount = _registry.marginAccount();
}
```

Acknowledging but yes system heavily relies on the admins to do the right thing, the right way. We might remove several such upgradeability rights during a broader refactor of the entire system.

Downgrading to medium as this is largely admin related.
