# [M] Accommodation of Non-ERC20-Compliant Tokens

## Summary
Severity: Medium
Contest weight: 0.5933
Dataset id: 12379
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Though there is a standardized ERC-20 specification, many token contracts may not strictly follow the specification or have additional functionalities beyond the specification. In this section, we examine the transfer() routine and possible idiosyncrasies from current widely-used token contracts. In particular, we use the popular stablecoin, i.e., USDT, as our example. We show the related code snippet below. Specifically, the transfer() routine does not have a return value defined and implemented. However, the IERC20 interface has defined the transfer() interface with a bool return value. As a result, the call to transfer() may expect a return value. With the lack of return value of USDT's transfer(), the call will be unfortunately reverted.
```solidity
function transfer(address _to, uint _value) public onlyPayloadSize(2 * 32) {
    uint fee = (_value.mul(basisPointsRate)).div(10000);
    if (fee > maximumFee) {
        fee = maximumFee;
    }
    uint sendAmount = _value.sub(fee);
    balances[msg.sender] = balances[msg.sender].sub(_value);
    balances[_to] = balances[_to].add(sendAmount);
    if (fee > 0) {
        balances[owner] = balances[owner].add(fee);
        Transfer(msg.sender, owner, fee);
    }
    Transfer(msg.sender, _to, sendAmount);
}
```
Because of that, a normal call to transfer() is suggested to use the safe version, i.e., safeTransfer(), In essence, it is a wrapper around ERC20 operations that may either throw on failure or return false without reverts. Moreover, the safe version also supports tokens that return no value (and instead revert or throw on failure). Note that non-reverting calls are assumed to be successful. In current implementation, if we examine the KratosTreasury::incurDebt() routine that is designed to allow approved addresses to borrow reserves. To accommodate the specific idiosyncrasy, there is a need to use safeTransfer(), instead of transfer() (line 398).
```solidity
function incurDebt(uint _amount, address _token) external {
    require(isDebtor[msg.sender], "Not approved");
    require(isReserveToken[_token], "Not accepted");
    uint value = valueOf(_token, _amount);
    uint maximumDebt = IERC20(MEMOries).balanceOf(msg.sender); // Can only borrow against sOHM held
    uint availableDebt = maximumDebt.sub(debtorBalance[msg.sender]);
    require(value <= availableDebt, "Exceeds debt limit");
    debtorBalance[msg.sender] = debtorBalance[msg.sender].add(value);
    totalDebt = totalDebt.add(value);
    totalReserves = totalReserves.sub(value);
    emit ReservesUpdated(totalReserves);
    IERC20(_token).transfer(msg.sender, _amount);
    emit CreateDebt(msg.sender, _token, _amount, value);
}
```

## Recommendation
Accommodate the above-mentioned idiosyncrasy about ERC20-related approve()/transfer()/transferFrom().
