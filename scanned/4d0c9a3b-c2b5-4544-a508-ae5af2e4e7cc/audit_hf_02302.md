# [M] Confused Spender Allowance In revokeGrant()

## Summary
Severity: Medium
Contest weight: 0.4419
Dataset id: 12558
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function revokeGrant(address grantHolder) external onlyGrantor returns (bool) {
    tokenGrant storage grant = _tokenGrants[grantHolder];
    vestingSchedule storage vesting = _vestingSchedules[grant.vestingLocation];
    uint256 notVestedAmount;
    // Make sure grantor can only revoke from own pool.
    require(msg.sender == owner() || msg.sender == grant.grantor, "ERC20Vestable: not allowed");
    // Make sure a vesting schedule has previously been set.
    require(grant.isActive, "ERC20Vestable: no active vesting schedule");
    // Make sure it's revocable.
    require(vesting.isRevocable, "ERC20Vestable: irrevocable");
    // Fail on likely erroneous input.
    uint32 _today = today();
    require(_today <= grant.startDay + vesting.duration, "ERC20Vestable: no effect");
    notVestedAmount = _getNotVestedAmount(grantHolder, _today);
    // Use ERC20 _approve() to forcibly approve grantor to take back not-vested tokens from grantHolder.
    _approve(grantHolder, grant.grantor, notVestedAmount);
    /* Emits an Approval Event. */
    transferFrom(grantHolder, grant.grantor, notVestedAmount);
    /* Emits a Transfer and an Approval Event. */
    // Kill the grant
    _tokenGrants[grantHolder] = _tokenGrants[address(0)];
    emit GrantRevoked(grantHolder, _today);
    /* Emits the GrantRevoked event. */
    return true;
}
```
The above logic executes as expected if the caller is the grantor. However, if it is invoked by the contract owner, the forced _approve() (line 440) is exercised on the grantor, instead of the current msg.sender, which may immediately fail the next transferFrom() statement (line 442).

## Recommendation
Revise the above aﬀected routine by specifying the right approval target.
