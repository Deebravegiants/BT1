# [H] Protocol fee from Market.sol is locked in MarketFactory

## Summary
Severity: High
Contest weight: 0.7506
Dataset id: 20258
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Here is MarketFactory#fund function:
```solidity
function fund(IMarket market) external {
    if (!instances(IInstance(address(market)))) revert FactoryNotInstanceError();
    market.claimFee();
}
```
This is Market#claimFee function:
```solidity
function claimFee() external {
    Global memory newGlobal = _global.read();
    if (_claimFee(address(factory()), newGlobal.protocolFee))
    ...
}
```
This is the internal _claimFee function:
```solidity
if (msg.sender != receiver) return false;
emit FeeClaimed(receiver, fee);
return true;
```
As we can see, when MarketFactory#fund is called, Market#claimFee gets called which will send the protocolFee to msg.sender(MarketFactory). When you check through the MarketFactory contract, there is no place where another address(such as protocol multisig, treasury or an EOA) is approved to spend MarketFactory's funds, and also, there is no function in the contract that can be used to transfer MarketFactory's funds. This causes locking of the protocol fees. Protocol fees cannot be withdrawn.

## Recommendation
Consider adding a withdraw function that protocol can use to get the protocolFee out of the contract. You can have the withdraw function transfer the MarketFactory balance to the treasury or something.
