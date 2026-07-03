Audit Report

## Title
Unbounded Withdrawal Queue Stuffing Enables Temporary Freezing of Legitimate User Withdrawals - (File: contracts/LRTWithdrawalManager.sol)

## Summary
`LRTWithdrawalManager.initiateWithdrawal` imposes no per-user cap on queued withdrawal requests. Because `_unlockWithdrawalRequests` processes the global queue strictly in FIFO order and `completeWithdrawal` enforces that a user's nonce is below `nextLockedNonce[asset]`, an attacker who fills the queue with minimum-amount requests ahead of a legitimate user forces the operator to exhaust all preceding entries before the legitimate user's request can be unlocked or claimed.

## Finding Description
`initiateWithdrawal` transfers rsETH from the caller and appends a new entry to the global nonce sequence with no per-user limit:

```solidity
// L162-163: only minimum-amount guard, no per-user cap
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
```

Each call increments the global nonce via `_addUserWithdrawalRequest` (L756-757). The total queue depth is bounded by `getAvailableAssetAmount` (L170, L599-603), which equals `totalAssets - assetsCommitted[asset]`, so the attacker can queue at most `totalAssets / minRsEthAmountToWithdraw` entries — potentially thousands for a high-TVL protocol with a small minimum.

`_unlockWithdrawalRequests` (L790-815) iterates strictly from `nextLockedNonce[asset]` forward and cannot skip entries. `completeWithdrawal` then enforces:

```solidity
// L707
if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
```

Any legitimate user whose nonce falls after the attacker's block of entries cannot claim until every preceding attacker nonce has been processed. The operator controls `firstExcludedIndex` per call, so gas per call is bounded, but the honest user remains locked for as many operator batches as it takes to drain the attacker's entries. `KernelDepositPool.initiateWithdrawal` already applies the analogous fix at L323 (`maxNumberOfWithdrawalsPerUser`), confirming the protocol is aware of this pattern.

## Impact Explanation
Legitimate users whose nonces fall after the attacker's entries cannot call `completeWithdrawal` — it reverts with `WithdrawalLocked` — until the operator processes all preceding attacker nonces. This constitutes **temporary freezing of funds** (Medium). Additionally, each `unlockQueue` batch that traverses attacker entries consumes disproportionate gas relative to legitimate work, constituting **unbounded gas consumption** (Medium) across the sequence of required operator calls.

## Likelihood Explanation
The attack requires the attacker to commit real rsETH equal to `K × minRsEthAmountToWithdraw[asset]`, bounded by total protocol TVL. The capital is recoverable (returned when attacker requests are eventually processed), so the cost is opportunity cost plus gas. A single address can execute the attack without Sybil mechanics. Given recoverable capital and a public entry point, likelihood is medium.

## Recommendation
1. Enforce a per-user cap on pending withdrawal requests per asset, analogous to `KernelDepositPool`'s `maxNumberOfWithdrawalsPerUser` check at L323.
2. Alternatively, allow `unlockQueue` to accept an explicit starting nonce so the operator can skip a contiguous range of attacker entries and unlock later legitimate requests out-of-order.
3. Raise `minRsEthAmountToWithdraw` to increase the capital cost of stuffing.

## Proof of Concept
1. Attacker acquires `K × minRsEthAmountToWithdraw[ETH]` rsETH (single address or multiple).
2. Attacker calls `initiateWithdrawal(ETH, minRsEthAmountToWithdraw[ETH], "")` K times, inserting entries at nonces 0…K-1. Each call passes the `getAvailableAssetAmount` check and increments `assetsCommitted`.
3. Honest user calls `initiateWithdrawal`, receiving nonce K.
4. Operator calls `unlockQueue` in batches. Each batch advances `nextLockedNonce[asset]` through attacker entries. Until all K attacker nonces are processed, `nextLockedNonce[asset] <= K`.
5. Honest user calls `completeWithdrawal`; L707 reverts with `WithdrawalLocked` because `K >= nextLockedNonce[asset]`.
6. Honest user's ETH remains inaccessible until the operator exhausts all K attacker entries across potentially many batched `unlockQueue` calls.