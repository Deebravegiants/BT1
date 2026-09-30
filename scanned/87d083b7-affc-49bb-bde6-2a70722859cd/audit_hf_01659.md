# [H] Faulty deposit_for() check

## Summary
Severity: High
Contest weight: 0.8857
Dataset id: 8982
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The claim() function in the RewardsDistributor contract is designed to claim rewards for vePeg locks. It transfers rewards directly if the lock is expired or calls the vePeg.deposit_for() function if the lock is not expired or is perpetually locked:
```solidity
function claim(uint256 _tokenId) external returns (uint256) {
    //...
    if (amount != 0) {
        //...
        if (locked.end > block.timestamp || locked.perpetuallyLocked) {
            // lock has not expired
            ve.deposit_for(_tokenId, amount);
        } else {
            // lock expired
            address owner = ve.ownerOf(_tokenId);
            token.safeTransfer(owner, amount);
        }
        //...
    }
    //...
```
The issue arises with perpetual locks. The deposit_for() function checks if lock.end > block.timestamp, but for perpetual locks, the lock's end time is always set to zero, which is considered expired by the implemented check in the deposit_for() function. This causes the deposit_for() function to revert when attempting to deposit rewards for perpetual locks:
```solidity
function deposit_for(uint256 _tokenId, uint256 _value) external nonreentrant {
    LockedBalance memory _locked = locked[_tokenId];
    //...
    require(
        _locked.end > block.timestamp,
        "Cannot add to expired lock. Withdraw"
    );
    //...
```
As a result, perpetual locks cannot receive their rewards, preventing them from increasing their voting power by the amount claimed. The only workaround is for the owner to unlock the perpetual lock using the unlock_perpetual() function.

## Recommendation
Update the deposit_for() function to correctly handle perpetual locks by checking their status and updating the perpetuallyLockedBalance accordingly:
```solidity
function deposit_for(uint256 _tokenId, uint256 _value) external nonreentrant {
    LockedBalance memory _locked = locked[_tokenId];
    //...
    - require
    - (_locked.end > block.timestamp, "Cannot add to expired lock. Withdraw");
    + require
    + (_locked.end > block.timestamp || _locked.perpetuallyLocked, "Cannot add to expired");
    + if (_locked.perpetuallyLocked) {
    +     perpetuallyLockedBalance += _value;
    + }
    //...
```
