# [M] Improved Logic For Same Transaction Deposit() And Withdraw() Handling In AutoBabyPool

## Summary
Severity: Medium
Contest weight: 0.4600
Dataset id: 11699
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.10, the AutoBabyPool contract aims to provide incentives so that users can stake and lock their funds in a stake pool. If we compare with other staking contracts, the BABY staked into this snack pool will be automatically compounded (or reinvested). An unstaking fee applies when the user unstakes within 3 days of staking. While examining the logic, we notice an exploiter could deposit() and withdraw() in one transaction and earn BABYs as long as _earn() delivers enough rewards. To elaborate, we show below the deposit() and withdraw() routines from AutoBabyPool.
```solidity
function deposit(uint256 _amount)
    external
    whenNotPaused
    notContract
    nonReentrant("deposit")
{
    require(_amount > 0, "Nothing to deposit");
    uint256 pool = balanceOf();
    token.safeTransferFrom(msg.sender, address(this), _amount);
    uint256 currentShares = 0;
    if (totalShares != 0) {
        currentShares = (_amount.mul(totalShares)).div(pool);
    } else {
        currentShares = _amount;
    }
    UserInfo storage user = userInfo[msg.sender];
    user.shares = user.shares.add(currentShares);
    user.lastDepositedTime = block.timestamp;
    totalShares = totalShares.add(currentShares);
    user.cakeAtLastUserAction = user.shares.mul(balanceOf()).div(totalShares);
    user.lastUserActionTime = block.timestamp;
    _earn();
    emit Deposit(msg.sender, _amount, currentShares, block.timestamp);
}
function withdraw(uint256 _shares)
    public
    notContract
    nonReentrant("withdraw")
{
    UserInfo storage user = userInfo[msg.sender];
    require(_shares > 0, "Nothing to withdraw");
    require(_shares <= user.shares, "Withdraw amount exceeds balance");
    uint256 currentAmount = (balanceOf().mul(_shares)).div(totalShares);
    user.shares = user.shares.sub(_shares);
    totalShares = totalShares.sub(_shares);
    uint256 bal = available();
    if (bal < currentAmount) {
        uint256 balWithdraw = currentAmount.sub(bal);
        IMasterChef(masterchef).leaveStaking(balWithdraw);
        uint256 balAfter = available();
        uint256 diff = balAfter.sub(bal);
        if (diff < balWithdraw) {
            currentAmount = bal.add(diff);
        }
    }
    if (block.timestamp < user.lastDepositedTime.add(withdrawFeePeriod)) {
        uint256 currentWithdrawFee = currentAmount.mul(withdrawFee).div(10000);
        token.safeTransfer(treasury, currentWithdrawFee);
        currentAmount = currentAmount.sub(currentWithdrawFee);
    }
    if (user.shares > 0) {
        user.cakeAtLastUserAction = user.shares.mul(balanceOf()).div(totalShares);
    } else {
        user.cakeAtLastUserAction = 0;
    }
    user.lastUserActionTime = block.timestamp;
    token.safeTransfer(msg.sender, currentAmount);
    emit Withdraw(msg.sender, currentAmount, _shares);
}
```
Our analysis shows that a bad actor makes a profit as long as there is enough reward accumulated from MasterChef (e.g. being idle for a long time without harvest() or other actions). The calling of _earn() (line 171) from deposit() could give more rewards than the currentWithdrawFee (line 384), thus covering the cost for the one transaction deposit() and withdraw().

## Recommendation
Improve the logic for same transaction deposit() and withdraw() handling in the AutoBabyPool contract.
