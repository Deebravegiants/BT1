# [H] All funds can be stolen from JOJODealer

## Summary
Severity: High
Contest weight: 0.7582
Dataset id: 22391
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Funding._withdraw() makes arbitrary call with user specified params. User can for example make ERC20 to himself and steal funds.
User can specify parameters param and to when withdraws:
```solidity
function executeWithdraw(address from, address to, bool isInternal, bytes memory param) external nonReentrant {
    Funding.executeWithdraw(state, from, to, isInternal, param);
}
```
In the end of _withdraw() function address to is called with that bytes param:
```solidity
function _withdraw(
    Types.State storage state,
    address spender,
    address from,
    address to,
    uint256 primaryAmount,
    uint256 secondaryAmount,
    bool isInternal,
    bytes memory param
)
    private
{
    ...
    if (param.length != 0) {
        require(Address.isContract(to), "target is not a contract");
        (bool success,) = to.call(param);
        if (success == false) {
            assembly {
                let ptr := mload(0x40)
                let size := returndatasize()
                returndatacopy(ptr, 0, size)
                revert(ptr, size)
            }
        }
    }
}
```
As an attack vector attacker can execute withdrawal of 1 wei to USDC contract and pass calldata to transfer arbitrary USDC amount to himself via USDC contract.
All funds can be stolen from JOJODealer

## Recommendation
Don't make arbitrary call with user specified params
