# [M] Improved Airdrop Logic in AirdropClaim::setUserInfo()

## Summary
Severity: Medium
Contest weight: 0.4196
Dataset id: 13259
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function setUserInfo(address _who, address _to, uint256 _amount) external onlyMerkle nonReentrant returns(bool status) {
    require(_who != address(0), "addr 0");
    require(_to != address(0), "addr 0");
    require(_amount > 0, "amnt 0");
    require(usersFlag[_who] == false, "!flag");
    require(init, "not init");
    uint256 _vestedAmount = _amount * VESTED_SHARE / PRECISION;
    uint256 _theInstantAmount = _amount * LINEAR_DISTRO / PRECISION;
    uint256 _theLockedLinearAmount = _theInstantAmount;
    uint256 _tokenPerSec = _theLockedLinearAmount * PRECISION / DISTRIBUTION_PERIOD;
    UserInfo memory _user = UserInfo({
        totalAmount: _amount,
        initAmount: _theInstantAmount,
        vestedAmount: _vestedAmount,
        lockedAmount: _theLockedLinearAmount,
        tokenPerSec: _tokenPerSec,
        lastTimestamp: startTimestamp,
        claimed: _theInstantAmount + _vestedAmount,
        to: _to
    });
    users[_who] = _user;
    usersFlag[_who] = true;
    // send out init amount
    token.safeTransfer(_to, _theInstantAmount);
    token.approve(ve, 0);
    token.approve(ve, _vestedAmount);
    IVotingEscrow(ve).create_lock_for(_vestedAmount, 2 * 364 * 86400, _who);
}
```

## Recommendation
Improve the above airdrop Logic by computing the right lockedAmount.
