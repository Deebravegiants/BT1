# [M] Improved Validation in requestWithdraw()

## Summary
Severity: Medium
Contest weight: 0.4391
Dataset id: 13151
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Synclub's Liquid Staking protocol has a core SnStakeManager contract that allows users to stake and unstake. While reviewing the current unstaking logic, we notice the related implementation needs to be improved. To elaborate, we show below the core requestWithdraw() routine. As the name indicates, this routine allows staking users to unstake. However, it restricts the available totalBnbToWithdraw to be no larger than totalDelegated, which somehow excludes the amountToDelegate amount. This may put unnecessary restrictions on staking users. For example, suppose the following case of having one single user Alice who just deposited 100 BNB (via deposit()) and there is no delegate() yet. Alice found out that it is now impossible to withdraw the staked 100 BNB back even the funds are not actually delegated yet.

```solidity
function requestWithdraw(uint256 _amountInSnBnb)
    external
    override
    whenNotPaused
{
    require(_amountInSnBnb > 0, "Invalid Amount");
    totalSnBnbToBurn += _amountInSnBnb;
    uint256 totalBnbToWithdraw = convertSnBnbToBnb(totalSnBnbToBurn);
    require(
        totalBnbToWithdraw <= totalDelegated,
        "Not enough BNB to withdraw"
    );
    userWithdrawalRequests[msg.sender].push(
        WithdrawalRequest({
            uuid: nextUndelegateUUID,
            amountInSnBnb: _amountInSnBnb,
            startTime: block.timestamp
        })
    );
    IERC20Upgradeable(snBnb).safeTransferFrom(
        msg.sender,
        address(this),
        _amountInSnBnb
    );
    emit RequestWithdraw(msg.sender, _amountInSnBnb);
}
```

## Recommendation
Revisit the unstake logic to ensure user funds can be fully withdrawn in all possible cases.
