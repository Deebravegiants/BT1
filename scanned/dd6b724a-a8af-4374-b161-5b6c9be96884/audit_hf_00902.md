# [H] Attacker can DoS user withdrawals at no cost

## Summary
Severity: High
Contest weight: 0.7828
Dataset id: 2664
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Everytime a user deposits or mints, a lockup element is added to an array. An attacker can deposit on behalf of other user and fill the array with excessive elements such that it is DoSed due to OOG.
sYUSD::deposit() is as follows:
```solidity
function _deposit(
    address caller,
    address receiver,
    uint256 assets,
    uint256 shares
) internal virtual override {
    super._deposit(caller, receiver, assets, shares);
    // Add new locked shares entry
    userLockedShares[receiver].push(LockedShares({
        amount: shares,
        expiryTimestamp: block.timestamp + lockupPeriod
    }));
}
```
As can be seen, it pushes a new element each time it is called, via sYUSD::deposit() or sYUSD::mint(). An attacker can deposit to another user and fill their array. Then, when the user withdraws via sYUSD::withdraw() or sYUSD::redeem(), it loops through the array all at once and DoSes withdrawals due to OOG.
```solidity
function _withdraw(
    address caller,
    address receiver,
    address owner,
    uint256 assets,
    uint256 shares
) internal virtual override {
    // First update the unlocked shares
    updateUnlockedShares(owner);
    // Ensure user has enough unlocked shares
    if (unlockedShares[owner] < shares) {
        revert InsufficientUnlockedShares(shares, unlockedShares[owner]);
    }
    // Reduce unlocked shares
    unlockedShares[owner] -= shares;
    super._withdraw(caller, receiver, owner, assets, shares);
}
...
function updateUnlockedShares(address user) public {
    LockedShares[] storage userLocks = userLockedShares[user];
    for (uint256 i = 0; i < userLocks.length; i++) {
        if (block.timestamp >= userLocks[i].expiryTimestamp && userLocks[i].amount > 0) {
            unlockedShares[user] += userLocks[i].amount;
            userLocks[i].amount = 0;
        }
    }
    // Clean up empty entries
    _cleanupLockedShares(user);
}
```
Please find a POC here.
Stuck funds at no cost for an attacker.

## Recommendation
Set a max iterations argument.
