# [H] Improper Borrow Interest Calculation In userReturn()

## Summary
Severity: High
Contest weight: 0.6354
Dataset id: 13238
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
By design, the ThemisBorrowCompound contract is one of the main entries for interaction with users. In particular, one entry routine, i.e., userReturn(), is used by the borrower to repay the borrowed assets, in order to redeem the collateral UniswapV3 position. While examining its logic, we notice the borrowed interests calculation needs to be improved.
To elaborate, we show below the related code snippet of the ThemisBorrowCompound contract. In the userReturn() function, the borrowed interests is calculated as below: uint256 _borrowInterests = _borrowPool.globalBowShare.sub(_borrowInfo.startBowShare).mul(_borrowInfo.amount).div(1e12) (line 244). We notice the _borrowPool.globalBowShare is not updated to the latest, but is updated in the _upGobalBorrowInfo() function (line 256) called inside the userReturn() function subsequently, which results inaccurate borrowed interests calculation. Given this, we suggest to update the _borrowPool.globalBowShare to the latest before calculating the borrowed interests.
```solidity
function userReturn(uint256 bid) public {
    require(!isBorrowOverdue(bid), "borrow is overdue");
    BorrowInfo storage _borrowInfo = borrowInfo[bid];
    require(_borrowInfo.user == msg.sender, "not owner");
    CompoundBorrowPool memory _borrowPool = borrowPoolInfo[_borrowInfo.pid];
    BorrowUserInfo storage _user = borrowUserInfos[msg.sender][_borrowInfo.pid];
    uint256 _borrowInterests = _borrowPool.globalBowShare.sub(_borrowInfo.startBowShare).mul(_borrowInfo.amount).div(1e12);
    uint256 _totalReturn = _borrowInfo.amount.add(_borrowInterests);
    public uint256 _userBalance = IERC20(_borrowPool.token).balanceOf(msg.sender);
    require(_userBalance >= _totalReturn, "not enough amount.");
    _borrowInfo.returnBlock = block.number;
    _borrowInfo.interests = _borrowInterests;
    _borrowInfo.state = 2;
    _upGobalBorrowInfo(_borrowInfo.pid, _borrowInfo.amount, 2);
    _updateRealReturnInterest(_borrowInfo.pid, _borrowInterests);
    uniswapV3.transferFrom(address(this), msg.sender, _borrowInfo.tokenId);
    _user.currTotalBorrow = _user.currTotalBorrow.sub(_borrowInfo.amount);
    _holderBorrowIds[msg.sender][_borrowInfo.pid].remove(bid);
    if(_user.currTotalBorrow == 0){
        _holderBorrowPoolIds[msg.sender].remove(_borrowInfo.pid);
    }
    IERC20(_borrowPool.token).safeTransferFrom(msg.sender, address(this), _totalReturn);
    IERC20(_borrowPool.token).safeTransfer(address(lendCompound), _borrowInfo.amount);
    emit UserReturn(msg.sender, bid, _borrowInfo.pid, _borrowInfo.amount, _borrowInterests);
}
```
Note other routines, i.e., transferToAuction(), isBorrowOverdue(), and pendingReturnInterests(), share the same issue.

## Recommendation
Correct the implementation of the above-mentioned routines.
