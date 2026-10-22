# [H] Incorrect Token Flow in withdraw()

## Summary
Severity: High
Contest weight: 0.6361
Dataset id: 12457
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The WombatPoolHelper is a helper smart contract to interact with WombatStaking (to provide liquidity on Wombat Exchange, etc.) and MasterMagpie (to stake LP token as a certificate and farm). While examining the token flow to withdraw assets from WombatPoolHelper, we notice the existence of incorrect token flow between WombatPoolHelper and WombatStaking which needs to be corrected.

To elaborate, we show below the code snippets of the WombatPoolHelper:withdraw() and WombatStaking:withdraw() routines. As implemented, the WombatPoolHelper:withdraw() takes the input _amount of receiptToken and unstakes it from MasterMagpie (line 137). The unstaked receiptToken _amount is then taken by invoking the WombatStaking:withdraw() (line 140). However, in the WombatStaking:withdraw() implementation, the input _amount is expected to be the amount of stables (_depositToken) which will be provided to Wombat Exchange as liquidity. Our analysis shows that, the WombatPoolHelper:withdraw() could be refactored to take the input _amount as the amount of the stables to withdraw which is the same as the WombatPoolHelper:deposit() where the input _amount represents the amount of the stables to deposit. With this, the WombatPoolHelper:withdraw() shall convert the input _amount of the stables to the amount of receiptToken which is needed to unstake from the MasterMagpie.

```solidity
function withdraw(uint256 _amount, uint256 _minAmount) external override _harvest {
    _unstake(_amount, msg.sender);
    IWombatStaking(wombatStaking).withdraw(
        depositToken,
        _amount,
        _minAmount,
        msg.sender
    );
    emit NewWithdraw(msg.sender, _amount);
}

function withdraw(
    address _depositToken,
    uint256 _amount,
    uint256 _minAmount,
    address _sender
) public _onlyPoolHelper(_depositToken) {
    // _amount is the amount of stable
    Pool storage poolInfo = pools[_depositToken];
    uint256 sharesAmount = getSharesForDepositTokens(_amount, _depositToken);
    uint256 lpAmount = getLPTokensForShares(sharesAmount, _depositToken);
    IMintableERC20(poolInfo.receiptToken).burn(msg.sender, sharesAmount);
    IERC20(poolInfo.lpAddress).approve(poolInfo.depositTarget, lpAmount);
    IMasterWombat(masterWombat).withdraw(poolInfo.pid, lpAmount);
    uint256 beforeWithdraw = IERC20(_depositToken).balanceOf(address(this));
    IWombatPool(poolInfo.depositTarget).withdraw(
        _depositToken,
        lpAmount,
        _minAmount,
        address(this),
        block.timestamp
    );
    poolInfo.size = _amount;
    poolInfo.sizeLp = lpAmount;
    IERC20(_depositToken).safeTransfer(
        _sender,
        IERC20(_depositToken).balanceOf(address(this)) - beforeWithdraw
    );
    emit NewWithdraw(_sender, _depositToken, _amount);
}
```

## Recommendation
Revised the WombatPoolHelper:withdraw() to correct the token flow during assets withdrawal.
