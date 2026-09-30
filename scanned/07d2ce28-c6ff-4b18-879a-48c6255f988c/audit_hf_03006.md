# [M] `getNextValidator

## Summary
Severity: Medium
Contest weight: 0.6304
Dataset id: 16784
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a denial‑of‑service (DoS) vulnerability in its depositEther() routine. The function iterates over a number of pending deposits and, for each iteration, obtains validator data by calling getNextValidator(). This helper reads the next entry from a pool of free validator slots. If the pool has been exhausted or if a previously‑used validator key is still present in the pool, getNextValidator() throws an exception, causing the entire loop – and therefore the whole depositEther() call – to revert. The root cause is the absence of defensive handling for the situation where the free‑validator list is empty or contains a duplicate entry; the contract assumes that every call to getNextValidator() will succeed and does not verify that the returned public key is unique before proceeding. An attacker (or an honest user) can trigger the failure simply by depositing when the free‑validator count is zero or by submitting a deposit that references a validator already marked as active. Because the revert aborts the whole transaction, no new ETH can be deposited, effectively freezing the deposit functionality until a privileged governor manually removes the offending validator entry with popValidators(). From the user’s perspective, attempts to deposit Ether result in a transaction that reverts with no obvious on‑chain error message, leading to a perception that “my deposit fails” or “my funds disappear” even though no ETH is transferred. The impact is limited to the deposit pathway – users cannot add new funds, and the protocol may miss expected inflows, harming liquidity and potentially breaking downstream accounting that assumes deposits are always processed. The issue was discovered during a formal audit when the test suite exercised depositEther() with a pre‑populated validator list and observed an unexpected revert. It is hard to notice in production because the revert only occurs under a specific state (empty validator buffer) and the contract does not emit a distinct event indicating the lack of free validators. To remediate, the contract should validate the availability of a free validator before entering the loop, guard the getNextValidator() call with try/catch (or equivalent error handling) to skip unavailable entries, and maintain a safety margin of unused validators. Additionally, the registry should enforce that the validator mapping is synchronized with the pool size, preventing duplicate entries from being considered free. By treating the condition as a class of “unchecked external data source leading to revert‑induced DoS”, the fix restores robustness without altering the core deposit logic.

## Proof of Concept
In `depositEther()`, if the `pubKey` is already used, the whole loop will revert, and the deposit operation cannot move on.
    
```solidity
// src/frxETHMinter.sol
function depositEther() external nonReentrant {
    // ...

    for (uint256 i = 0; i < numDeposits; ++i) {
        // Get validator information
        (
            bytes memory pubKey,
            bytes memory withdrawalCredential,
            bytes memory signature,
            bytes32 depositDataRoot
        ) = getNextValidator(); // Will revert if there are not enough free validators

        // Make sure the validator hasn't been deposited into already, to prevent stranding an extra 32 eth
        // until withdrawals are allowed
        require(!activeValidators[pubKey], "Validator already has 32 ETH");
    // ...        
}
```

And in the next rewards cycle, `lastRewardAmount` will be linearly added to `storedTotalAssets`, their sum is the return value of `totalAssets()`:
    
```solidity
function totalAssets() public view override returns (uint256) {
    // ...

    if (block.timestamp >= rewardsCycleEnd_) {
        // no rewards or rewards fully unlocked
        // entire reward amount is available
        return storedTotalAssets_ + lastRewardAmount_;
    }

    // rewards not fully unlocked
    // add unlocked rewards to stored total
    uint256 unlockedRewards = (lastRewardAmount_ * (block.timestamp - lastSync_)) / (rewardsCycleEnd_ - lastSync_);
    return storedTotalAssets_ + unlockedRewards;
}
```

Temporarily the `depositEther()` function will be inaccessible. Until the governance calls the registry to pop the wrong validator.
    
```solidity
// src/OperatorRegistry.sol
function popValidators(uint256 times) public onlyByOwnGov {
    // Loop through and remove validator entries at the end
    for (uint256 i = 0; i < times; ++i) {
        validators.pop();
    }

    emit ValidatorsPopped(times);
}
```

## Recommendation
Use `try/catch` to skip the wrong validator, then the deposit function will be more robust to unexpected situations.

We plan to keep an eye on the number of free validators and have a decent sized buffer of them.

Awarding as Medium, given that this can disable deposits, the registry should check against the mapping.
