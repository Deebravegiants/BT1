# [M] StakerVault.unstake

## Summary
Severity: Medium
Contest weight: 0.6031
Dataset id: 5843
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the StakerVault contract’s accounting of staked tokens across two distinct pools: one tracking the total amount staked by strategy contracts (strategiesTotalStaked) and another tracking the total amount staked by non‑strategy addresses (_poolTotalStaked). The root cause is that the contract does not update these counters when an address that previously held a non‑strategy balance is later approved as a strategy, nor does it adjust the counters when tokens are transferred between a strategy and a non‑strategy address. Consequently, the internal totals can become inconsistent, with strategiesTotalStaked being lower than the actual amount that should be attributed to strategies. When a user then attempts to unstake or call unstakeFor, the contract attempts to decrement strategiesTotalStaked by the requested amount. Because the counter is already too low, the subtraction underflows, triggering a Solidity runtime error and causing the transaction to revert. This underflow can also be triggered during transfers that cross the strategy boundary, as the transfer and transferFrom functions lack the necessary logic to rebalance the two totals. The impact is that users’ funds become permanently locked in the vault: the revert prevents any tokens from being returned, so from the user’s perspective the withdrawal transaction finishes with no tokens received, often described as a “refund missing” or “balance becomes zero”. The issue manifests under specific conditions – namely when a non‑strategy address is promoted to a strategy without moving its existing balance, or when a transfer occurs between a strategy and a non‑strategy address – and it can be exacerbated by a front‑running attacker who times a malicious addStrategy call to force the counters out of sync. The bug was discovered during a Code4rena audit, where the auditors traced the underflow path and identified that the contract’s invariant (the sum of strategiesTotalStaked and _poolTotalStaked should equal the total staked supply) is violated. The problem is subtle because the revert only occurs when the counters are mismatched, a state that may be rare in normal operation, making it hard to notice without targeted testing. To remediate the issue, the contract must reconcile the two totals whenever a strategy is added (by moving the address’s existing balance from the pool total to the strategy total) and must adjust the counters inside both transfer and transferFrom when tokens move across the strategy boundary. Implementing these changes restores the accounting invariant, eliminates the underflow risk, and prevents funds from becoming irretrievably stuck.

## Proof of Concept
Currently it saves totalStaked for strategies and non-strategies separately.

uint underflow error could occur in these cases.

Scenario 1.

  1. Address A(non-strategy) stakes some amount x and it will be added to StakerVault_poolTotalStaked.
  2. This address A is approved as a strategy by StakerVault.inflationManager.
  3. Address A tries to unstake amount x, it will be deducted from StakerVault.strategiesTotalStaked because this address is a strategy already.

Even if it would succeed for this strategy but it will revert for other strategies because StakerVault.strategiesTotalStaked is less than correct staked amount for strategies.

Scenario 2. There is a transfer between strategy and non-strategy using StakerVault.transfer(), StakerVault.transferFrom() functions. In this case, StakerVault.strategiesTotalStaked and StakerVault._poolTotalStaked must be changed accordingly but there is no such logic.

## Recommendation
You need to modify 3 functions. StakerVault.addStrategy(), StakerVault.transfer(), StakerVault.transferFrom().

  1. You need to move staked amount from StakerVault._poolTotalStaked to StakerVault.strategiesTotalStaked every time when StakerVault.inflationManager approves a new strategy.

You can modify addStrategy() at L98-L102 like this.

```solidity
function addStrategy(address strategy) external override returns (bool) {
    require(msg.sender == address(inflationManager), Error.UNAUTHORIZED_ACCESS);
    require(!strategies[strategy], Error.ADDRESS_ALREADY_SET);

    strategies[strategy] = true;
    _poolTotalStaked -= balances[strategy];
    strategiesTotalStaked += balances[strategy];

    return true;
}
```

  2. You need to add below code at L126 of transfer() function.

```solidity
if(strategies[msg.sender] != strategies[account]) {
    if(strategies[msg.sender]) {
        // from strategy to non-strategy
        _poolTotalStaked += amount;
        strategiesTotalStaked -= amount;
    } else {
        // from non-strategy to strategy
        _poolTotalStaked -= amount;
        strategiesTotalStaked += amount;
    }
}
```

  3. You need to add below code at L170 of transferFrom() function.

```solidity
if(strategies[src] != strategies[dst]) {
    if(strategies[src]) {
        // from strategy to non-strategy
        _poolTotalStaked += amount;
        strategiesTotalStaked -= amount;
    } else {
        // from non-strategy to strategy
        _poolTotalStaked -= amount;
        strategiesTotalStaked += amount;
    }
}
```

The warden has identified a way for funds to be stuck due to underflow.

While the odds of this happening are fairly low, the grief can be executed by frontrunning the `addStrategy` call, as well as by mistake.

Additionally, a strategy doesn’t seem to be removable making the loss of those hypothetical tokens permanent.

For those reasons I believe Medium Severity to be appropriate.
