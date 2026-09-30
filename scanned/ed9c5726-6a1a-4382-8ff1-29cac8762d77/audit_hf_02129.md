# [H] Incorrect walletTokenBalance Update In DuneLocker::lockTokens()

## Summary
Severity: High
Contest weight: 0.8056
Dataset id: 11960
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The DuneLocker contract provides an external lockTokens() function for users to lock a specified amount of ERC20 tokens into the contract. Only the specified withdrawer can withdraw these locked tokens when the lock time is due. Our analysis with this routine shows its current implementation is not correct.
To elaborate, we show below its code snippet. It comes to our attention that the wrong key is used when updating the state variable walletTokenBalance. Specifically, the second key used for updating the nested mapping state variable walletTokenBalance should be _withdrawer, instead of current msg.sender (line 52).
```solidity
function lockTokens(IERC20 _token , address _withdrawer , uint256 _amount , uint256 _unlockTimestamp) payable external returns (uint256 _id) {
    require(_amount > 0, "Token amount too low!");
    require(_unlockTimestamp < 10000000000 , "Unlock timestamp is not in seconds!");
    require(_unlockTimestamp > block.timestamp , "Unlock timestamp is not in the future!");
    require(_token.allowance(msg.sender , address(this)) >= _amount , "Approve tokens first!");
    require(msg.value >= lockFee , "Need to pay lock fee!");
    uint256 beforeDeposit = _token.balanceOf(address(this));
    _token.safeTransferFrom(msg.sender , address(this), _amount);
    uint256 afterDeposit = _token.balanceOf(address(this));
    _amount = afterDeposit.sub(beforeDeposit);
    payable(feeAddress).transfer(msg.value);
    walletTokenBalance[address(_token)][msg.sender] = walletTokenBalance[address(_token)][msg.sender].add(_amount);
    _id = ++depositsCount;
    lockedToken[_id].token = _token;
    lockedToken[_id].withdrawer = _withdrawer;
    lockedToken[_id].amount = _amount;
    lockedToken[_id].unlockTimestamp = _unlockTimestamp;
    lockedToken[_id].withdrawn = false;
    depositsByTokenAddress[address(_token)].push(_id);
    depositsByWithdrawer[_withdrawer].push(_id);
    emit Lock(address(_token), _amount , _id);
    return _id;
}
```

## Recommendation
Use the correct key when updating the state variable walletTokenBalance. An example revision is shown as follows:
```solidity
function lockTokens(IERC20 _token , address _withdrawer , uint256 _amount , uint256 _unlockTimestamp) payable external returns (uint256 _id) {
    require(_amount > 0, "Token amount too low!");
    require(_unlockTimestamp < 10000000000 , "Unlock timestamp is not in seconds!");
    require(_unlockTimestamp > block.timestamp , "Unlock timestamp is not in the future!");
    require(_token.allowance(msg.sender , address(this)) >= _amount , "Approve tokens first!");
    require(msg.value >= lockFee , "Need to pay lock fee!");
    uint256 beforeDeposit = _token.balanceOf(address(this));
    _token.safeTransferFrom(msg.sender , address(this), _amount);
    uint256 afterDeposit = _token.balanceOf(address(this));
    _amount = afterDeposit.sub(beforeDeposit);
    payable(feeAddress).transfer(msg.value);
    walletTokenBalance[address(_token)][_withdrawer] = walletTokenBalance[address(_token)][_withdrawer].add(_amount);
    _id = ++depositsCount;
    lockedToken[_id].token = _token;
    lockedToken[_id].withdrawer = _withdrawer;
    lockedToken[_id].amount = _amount;
    lockedToken[_id].unlockTimestamp = _unlockTimestamp;
    lockedToken[_id].withdrawn = false;
    depositsByTokenAddress[address(_token)].push(_id);
    depositsByWithdrawer[_withdrawer].push(_id);
    emit Lock(address(_token), _amount , _id);
    return _id;
}
```
