# [H] Revisited TransferHelper::safeTransferToken() Logic

## Summary
Severity: High
Contest weight: 0.7877
Dataset id: 12891
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Though there is a standardized ERC-20 specification, many token contracts may not strictly follow the specification or have additional functionalities beyond the specification. In this section, we examine the transfer() routine and possible idiosyncrasies from current widely-used token contracts. In particular, we use the popular stablecoin, i.e., USDT, as our example. We show the related code snippet below. Specifially, the transfer() routine does not have a return value defined and implemented. However, the IERC20 interface has defined the transfer() interface with a bool return value. As a result, the call to transfer() may expect a return value. With the lack of return value of USDT's transfer(), the call will be unfortunately reverted.
```solidity
function transfer(address _to, uint _value) public onlyPayloadSize(2 + 32 + 32) {
    uint fee = (_value.mul(basisPointsRate)).div(10000);
    if (fee > maximumFee) fee = maximumFee;
    uint sendAmount = _value.sub(fee);
    balances[msg.sender] = balances[msg.sender].sub(_value);
    balances[_to] = balances[_to].add(sendAmount);
    if (fee > 0) balances[owner] = balances[owner].add(fee);
    Transfer(msg.sender, owner, fee);
    Transfer(msg.sender, _to, sendAmount);
}
```
Because of that, a normal call to transfer() is suggested to use the safe version, i.e., safeTransfer(), In essence, it is a wrapper around ERC20 operations that may either throw on failure or return false without reverts. Moreover, the safe version also supports tokens that return no value (and instead revert or throw on failure). Note that non-reverting calls are assumed to be successful. In current implementation, if we examine the TransferHelper::safeTransferToken() routine that is designed to transfer the requested token to the intended recipient. To accommodate the specific idiosyncrasy, there is a need to revise the transfer error status as !(success && (data.length == 0 || abi.decode(data, bool))), instead of !success && (data.length == 0 || abi.decode(data, (bool))) (line 435).
```solidity
function safeTransferToken(
    address token,
    address to,
    uint256 value,
    bool raiseError
) internal returns (bool) {
    // bytes4(keccak256(bytes("transfer(address,uint256)")));
    (bool success, bytes memory data) = token.call(
        abi.encodeWithSelector(0xa9059cbb, to, value)
    );
    bool hasError = !success && (data.length == 0 || abi.decode(data, (bool)));
    if (hasError && raiseError) revert TransferHelper__TransferFailed();
    return !hasError;
}
```

## Recommendation
Revise the above logic to properly check the transfer status. The same issue is also applicable to the safeApprove() routine in the same contract. Note that the safeTransferFrom() routine implements the correct logic.
