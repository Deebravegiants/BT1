### Title
Zero-Minimum Withdrawal Queue Stuffing Delays Legitimate User Withdrawals - (File: contracts/LRTWithdrawalManager.sol)

### Summary

`LRTWithdrawalManager.initiateWithdrawal` has no enforced minimum withdrawal amount by default (`minRsEthAmountToWithdraw` initializes to zero for all assets). An unprivileged rsETH holder can create an unbounded number of dust withdrawal requests at 1-wei cost each, stuffing the global FIFO withdrawal queue and temporarily freezing legitimate users' queued funds.

### Finding Description

`initiateWithdrawal` enforces:

```solidity
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
```

`minRsEthAmountToWithdraw` is a plain mapping that defaults to `0` for every asset until an admin explicitly calls `setMinRsEthAmountToWithdraw`. When the default is in effect, the only guard is `rsETHUnstaked == 0`, meaning a caller can pass `rsETHUnstaked = 1` (1 wei of rsETH) and successfully enqueue a withdrawal request.

Each such call:
1. Transfers 1 wei rsETH from the attacker to the contract.
2. Computes `expectedAssetAmount ≈ 1 wei` and increments `assetsCommitted[asset]` by that amount.
3. Pushes a new entry into the global sequential nonce queue (`nextUnusedNonce[asset]++`).

The queue is processed strictly in FIFO order inside `_unlockWithdrawalRequests`:

```solidity
while (nextLockedNonce_ < firstExcludedIndex) {
    bytes32 requestId = getRequestId(asset, nextLockedNonce_);
    WithdrawalRequest storage request = withdrawalRequests[requestId];
    // ...
    unchecked { nextLockedNonce_++; }
}
nextLockedNonce[asset] = nextLockedNonce_;
```

Operators cannot skip nonces; they must advance `nextLockedNonce` through every dust entry before reaching legitimate requests submitted later. With 1 wei rsETH per request and a protocol TVL of, say, 100,000 ETH, an attacker can enqueue up to ~10^23 requests before the `assetsCommitted` ceiling is hit — far more than any operator can process in practice.

### Impact Explanation

Legitimate users who call `initiateWithdrawal` after the attacker's dust requests are placed behind all dust entries in the global queue. Their rsETH is locked in the contract and their expected assets are committed, but `unlockQueue` cannot reach their requests until every preceding dust entry is processed. This constitutes a **temporary freezing of funds** for all users who queue after the attack begins.

### Likelihood Explanation

The default value of `minRsEthAmountToWithdraw` is `0` for every asset. A newly deployed or upgraded contract is immediately vulnerable until an admin explicitly sets a minimum. An attacker needs only a trivial amount of rsETH (obtainable on the open market) and pays only gas per request. The attack is economically rational for any party wishing to delay competitors' withdrawals or grief the protocol.

### Recommendation

Set a non-zero `minRsEthAmountToWithdraw` for every supported asset during initialization (or in the initializer), rather than relying on a post-deployment admin call. Additionally, consider adding a per-user or global cap on the number of pending withdrawal requests to bound queue depth independently of the minimum amount.

### Proof of Concept

1. `minRsEthAmountToWithdraw[ETH_TOKEN]` is `0` (default, admin has not called `setMinRsEthAmountToWithdraw`).
2. Attacker holds `N` wei of rsETH (e.g., `N = 10_000`).
3. Attacker calls `initiateWithdrawal(ETH_TOKEN, 1, "")` in a loop `N` times. Each call succeeds because `1 >= minRsEthAmountToWithdraw[ETH_TOKEN]` (which is `0`) and `1 != 0`.
4. `nextUnusedNonce[ETH_TOKEN]` advances by `N`; `assetsCommitted[ETH_TOKEN]` increases by `N` wei.
5. Victim calls `initiateWithdrawal(ETH_TOKEN, 1 ether, "")` — their request is assigned nonce `N`.
6. Operator calls `unlockQueue(ETH_TOKEN, N+1, ...)`. The while-loop must iterate through all `N` dust entries before reaching the victim's entry at nonce `N`, consuming proportional gas and requiring multiple batched calls.
7. Victim's 1 ETH worth of rsETH remains locked in the contract until all `N` dust entries are processed. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L35-35)
```text
    mapping(address asset => uint256) public minRsEthAmountToWithdraw;
```

**File:** contracts/LRTWithdrawalManager.sol (L161-163)
```text
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
```

**File:** contracts/LRTWithdrawalManager.sol (L170-178)
```text
        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L330-333)
```text
    function setMinRsEthAmountToWithdraw(address asset, uint256 minRsEthAmountToWithdraw_) external onlyLRTAdmin {
        minRsEthAmountToWithdraw[asset] = minRsEthAmountToWithdraw_;
        emit MinAmountToWithdrawUpdated(asset, minRsEthAmountToWithdraw_);
    }
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
