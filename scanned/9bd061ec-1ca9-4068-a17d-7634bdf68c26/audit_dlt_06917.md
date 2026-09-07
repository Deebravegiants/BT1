# [H] GroupBuy can be drained of all ETH.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-12-tessera
Published: 2022-12-19
Source: https://github.com/code-423n4/2022-12-tessera-findings/issues/52
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-12-tessera/blob/f37a11407da2af844bbfe868e1422e3665a5f8e4/src/modules/GroupBuy.sol#L204-L219


# Vulnerability details

## Description


purchase() in GroupBuy faciilitates the purchasing of an NFT after enough contributions were gathered. Another report titled *"Attacker can steal the amount collected so far in the GroupBuy for NFT purchase*" describes a high impact bug in purchase. It is advised to read that first for context.

Additionally, purchase() is vulnerable to a re-entrancy exploit which can be *chained* or *not chained* to the \_market issue to steal *the entire* ETH stored in GroupBuy, rather than being capped to `minReservePrices[_poolId] * filledQuantities[_poolId]`. 

Attacker may take control of execution using this call:
```
// Executes purchase order transaction through market buyer contract and deploys new vault
address vault = IMarketBuyer(_market).execute{value: _price}(_purchaseOrder);
```
It could occur either by exploiting the unvalidated \_market vulnerability , or by abusing an existing market that uses a user address in \_purchaseOrder. 

There is no re-entrancy protection in purchase() call:
```
function purchase(
    uint256 _poolId,
    address _market,
    address _nftContract,
    uint256 _tokenId,
    uint256 _price,
    bytes memory _purchaseOrder,
    bytes32[] memory _purchaseProof
) external {
```

\_verifyUnsuccessfulState() needs to not revert for purchase call. It checks the pool.success flag:
`if (pool.success || block.timestamp > pool.terminationPeriod) revert InvalidState();`

However, success is only set as the last thing in purchase():

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-12-tessera-findings/issues/52_
