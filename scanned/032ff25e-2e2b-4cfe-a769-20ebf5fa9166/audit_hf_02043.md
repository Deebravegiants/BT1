# [M] Safe-Version Replacement With safeTransfer() And safeTransferFrom()

## Summary
Severity: Medium
Contest weight: 0.5931
Dataset id: 11637
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Though there is a standardized ERC-20 specification, many token contracts may not strictly follow the specification or have additional functionalities beyond the specification.
In this section, we examine the transfer() routine and possible idiosyncrasies from current widely-used token contracts.
In particular, we use the popular stablecoin, i.e., USDT, as our example.
We show the related code snippet below.
```solidity
* @dev transfer token for a specified address
* @param _to The address to transfer to.
* @param _value The amount to be transferred.
function transfer(address _to, uint _value) public onlyPayloadSize(2) {
    uint fee = (_value.mul(basisPointsRate)).div(10000);
    if (fee > maximumFee)
        fee = maximumFee;
    uint sendAmount = _value.sub(fee);
    balances[msg.sender] = balances[msg.sender].sub(_value);
    balances[_to] = balances[_to].add(sendAmount);
    if (fee > 0)
        balances[owner] = balances[owner].add(fee);
    Transfer(msg.sender, owner, fee);
    Transfer(msg.sender, _to, sendAmount);
}
```
It is important to note the transfer() function does not have a return value.
However, the ERC20Interface interface has defined the following transfer() interface with a bool return value:
function transfer(address to, uint tokens) virtual public returns (bool success).
As a result, the call to transfer() may expect a return value.
With the lack of return value of USDT's transfer(), the call will be unfortunately reverted.
Because of that, a normal call to transfer() is suggested to use the safe version, i.e., safeTransfer(),
In essence, it is a wrapper around ERC20 operations that may either throw on failure or return false without reverts.
Moreover, the safe version also supports tokens that return no value (and instead revert or throw on failure).
Note that non-reverting calls are assumed to be successful.
Similarly, there is a safe version of transferFrom() as well, i.e., safeTransferFrom().
In the following, we show the Charging_Transfer_ERC20() routine in the D_Swap contract.
If USDT is given as token, the unsafe version of ERC20Interface(token).transfer(to, exactly_amount) (line 400) may revert as there is no return value in the USDT token contract's transfer() implementation (but the ERC20Interface interface expects a return value)!
```solidity
function Charging_Transfer_ERC20(address token, address to, uint256 amount) private {
    (address tc_addr) = D_Swap_Main(m_DSwap_Main_Address).m_Trading_Charge_Lib();
    (address collecter_addr) = D_Swap_Main(m_DSwap_Main_Address).m_Address_of_Token_Collecter();
    uint256 exactly_amount = Trading_Charge(tc_addr).Amount(amount, to);
    bool res = true;
    if(exactly_amount >= 1)
        ERC20Interface(token).transfer(to, exactly_amount);
    if(amount.sub(exactly_amount) >= 1)
        ERC20Interface(token).transfer(collecter_addr, amount.sub(exactly_amount));
}
```
Note that other routines Receive_Token(), Deposit_For_Tail() and Withdraw_Head() share the same issue.

## Recommendation
Accommodate the above-mentioned idiosyncrasy about ERC20-related transfer()/transferFrom().
