Audit Report

## Title
Unbounded Withdrawal Request Queue Growth Causes Temporary Freezing of Other Users' Withdrawals — (`contracts/LRTWithdrawalManager.sol`)

## Summary
`initiateWithdrawal` imposes no per-user cap on the number of pending withdrawal requests, and `minRsEthAmountToWithdraw` defaults to zero (effective minimum: 1 wei). Because `_unlockWithdrawalRequests` advances `nextLockedNonce[asset]` strictly in FIFO order with no skip mechanism, an attacker who front-loads the queue with many small requests forces every subsequent user's withdrawal to wait until all preceding entries are processed.

## Finding Description
`initiateWithdrawal` at [1](#0-0)  checks only that `rsETHUnstaked >= minRsEthAmountToWithdraw[asset]`. Because `minRsEthAmountToWithdraw` is a plain mapping initialized to zero [2](#0-1)  and the `initialize` function never sets it [3](#0-2) , the effective floor is 1 wei of rsETH. There is no limit on how many times a single address may call the function.

Each call pushes a new entry into the global sequential queue via `_addUserWithdrawalRequest`: [4](#0-3) 

The operator's unlock path iterates from `nextLockedNonce[asset]` to `firstExcludedIndex` with no ability to skip or cancel individual entries: [5](#0-4) 

`nextLockedNonce[asset]` is only advanced by processing every entry in order. A legitimate user whose request lands at nonce N cannot have their request unlocked until all nonces 0 … N-1 have been iterated through, regardless of who owns them.

The `assetsCommitted` guard at [6](#0-5)  does not prevent queue bloat: with 1 wei rsETH per request, `expectedAssetAmount` rounds to ~1 wei, so an attacker with 1 rsETH (1 × 10¹⁸ wei) can enqueue up to 10¹⁸ requests before exhausting available assets. Even at realistic minimums (e.g., 0.01 ETH), a whale with 100 rsETH can create 10,000 requests.

## Impact Explanation
**Medium — Temporary freezing of funds.** Legitimate users who submit withdrawal requests after the attacker's entries cannot have their requests unlocked until the operator iterates through every preceding entry. The delay is directly proportional to the number of attacker-created entries and is entirely attacker-controlled. The operator cannot skip entries; each `unlockQueue` call is bounded by the block gas limit (~6,000 iterations per call at ~5,000 gas/iteration on a 30 M gas block), so processing 1 million dust entries requires ~167 separate operator transactions. This matches the allowed impact "Medium. Temporary freezing of funds."

## Likelihood Explanation
**Medium.** The attack is permissionless — any rsETH holder can execute it. `minRsEthAmountToWithdraw` defaults to zero, making the minimum 1 wei until an admin explicitly sets it. Even after a non-zero minimum is configured, a moderate rsETH holder can create thousands of entries. The attacker's rsETH is eventually returned (converted to the underlying asset), so the net cost is gas only, making the attack economically rational for a motivated griever.

## Recommendation
1. **Set a meaningful `minRsEthAmountToWithdraw` at initialization** and add a `require(min > 0)` guard in the setter to prevent it from being zeroed out.
2. **Cap pending requests per user per asset**, e.g.:
   ```solidity
   require(userAssociatedNonces[asset][msg.sender].length() < MAX_REQUESTS_PER_USER, "Too many pending requests");
   ```
3. **Allow the operator to cancel or skip stale/dust requests** so the queue cannot be permanently blocked by malicious entries.

## Proof of Concept
1. Deploy `LRTWithdrawalManager`; `minRsEthAmountToWithdraw[ETH]` is 0 (default).
2. Attacker holds 1 rsETH (1 × 10¹⁸ wei).
3. Attacker calls `initiateWithdrawal(ETH, 1, "")` repeatedly across many transactions, each advancing `nextUnusedNonce[ETH]` by 1 and committing 1 wei to `assetsCommitted[ETH]`. After N calls, the queue contains nonces 0 … N-1 owned by the attacker.
4. Legitimate user calls `initiateWithdrawal(ETH, 1 ether, "")` — succeeds, placed at nonce N.
5. Operator calls `unlockQueue(ETH, 6000, ...)` — processes nonces 0–5999 (all attacker dust). Legitimate user's request at nonce N remains locked.
6. Operator must repeat `unlockQueue` ⌈N/6000⌉ more times before reaching nonce N, delaying the legitimate user's withdrawal by an attacker-controlled number of operator transactions.

A Foundry fuzz test can confirm this by fuzzing the number of attacker `initiateWithdrawal` calls and asserting that `nextLockedNonce[asset]` never reaches the legitimate user's nonce until all preceding entries are processed.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L35-35)
```text
    mapping(address asset => uint256) public minRsEthAmountToWithdraw;
```

**File:** contracts/LRTWithdrawalManager.sol (L90-98)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        __Pausable_init();
        __ReentrancyGuard_init();
        withdrawalDelayBlocks = 8 days / 12 seconds;

        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L162-163)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
```

**File:** contracts/LRTWithdrawalManager.sol (L170-173)
```text
        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L755-757)
```text
        // Map the user to the newly created request index and increment the nonce for future requests.
        userAssociatedNonces[asset][msg.sender].pushBack(nextUnusedNonce_);
        nextUnusedNonce[asset] = nextUnusedNonce_ + 1;
```

**File:** contracts/LRTWithdrawalManager.sol (L790-815)
```text
        while (nextLockedNonce_ < firstExcludedIndex) {
            bytes32 requestId = getRequestId(asset, nextLockedNonce_);
            WithdrawalRequest storage request = withdrawalRequests[requestId];

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

            // Calculate the amount user will receive
            uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);

            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request

            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
            assetAmountToUnlock += payoutAmount;

            unlockedWithdrawalsCount[asset]++;

            unchecked {
                nextLockedNonce_++;
            }
        }
        nextLockedNonce[asset] = nextLockedNonce_;
```
