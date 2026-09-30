# [H] GroupBuy can be drained of all ETH.

## Summary
Severity: High
Contest weight: 0.8432
Dataset id: 17327
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`purchase()` in GroupBuy faciilitates the purchasing of an NFT after enough contributions were gathered. Another report titled _“Attacker can steal the amount collected so far in the GroupBuy for NFT purchase_ ” describes a high impact bug in purchase. It is advised to read that first for context.

Additionally, `purchase()` is vulnerable to a re-entrancy exploit which can be _chained_ or _not chained_ to the `_market` issue to steal _the entire_ ETH stored in GroupBuy, rather than being capped to `minReservePrices[_poolId] * filledQuantities[_poolId]`.

Attacker may take control of execution using this call:
```solidity
// Executes purchase order transaction through market buyer contract and deploys new vault
address vault = IMarketBuyer(_market).execute{value: _price}(_purchaseOrder);
```

It could occur either by exploiting the unvalidated `_market` vulnerability, or by abusing an existing market that uses a user address in `_purchaseOrder`.

There is no re-entrancy protection in `purchase()` call:
```solidity
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

`_verifyUnsuccessfulState()` needs to not revert for purchase call. It checks the pool.success flag: `if (pool.success || block.timestamp > pool.terminationPeriod) revert InvalidState();`

However, success is only set as the last thing in `purchase()`:
```solidity
// Stores mapping value of poolId to newly deployed vault
poolToVault[_poolId] = vault;
// Sets pool state to successful
poolInfo[_poolId].success = true;
// Emits event for purchasing NFT at given price
emit Purchase(_poolId, vault, _nftContract, _tokenId, _price);
```

Therefore, attacker can re-enter purchase() function multiple times, each time extracting the maximum allowed price. If attacker uses the controlled `_market` exploit, the function will return the current NFT owner, so when all the functions unwind they will keep setting success to true and exit nicely.

## Proof of Concept
1. GroupBuy holds 1500 ETH, from various bids
2. maximum allowed price (`minReservePrices[_poolId] * filledQuantities[_poolId]`) is 50 * 20 = 1000 ETH
3. purchase(1000 ETH) is called
   1. GroupBuy sends attacker 1000 ETH and calls `execute()`
      1. `execute()` calls purchase(500ETH)
         1. GroupBuy sends attacker 500 ETH and calls `execute()`
            1. execute returns NFT owner address
         2. GroupBuy sees returned address is NFT owner. Marks success and returns
      2. execute returns NFT owner address
   2. GroupBuy sees returned address is NFT owner. Marks success and returns
4. Attacker is left with 1500 ETH. Previous exploit alone can only net 1000ETH. Additionally, this exploit can be chained to any trusted MarketBuyer which passes control to user for purchasing and storing in vault, and then returns a valid vault.

## Recommendation
Add a re-entrancy guard to `purchase()` function. Also, change success variable before performing external contract calls.

Agree with High severity. Instead of adding `re-entrancy` tag to `purchase` function, pool state simply needs to be updated to `success` before execution.

In regards to:
or by abusing an existing market that uses a user address in _purchaseOrder.
This is not considered an issue since users will most likely NOT contribute to a pool where they are not familiar with the NFT and / or contract. Since the NFT contract is set when the pool is created, it should not matter whether the contract is malicious or is for an existing market that uses a user address, the pool will just be disregarded.

<https://github.com/fractional-company/modular-fractional/pull/201>

**Status:** Mitigation confirmed by [gzeon](https://github.com/code-423n4/2023-01-tessera-mitigation-findings/issues/48), [IllIllI](https://github.com/code-423n4/2023-01-tessera-mitigation-findings/issues/28), and [Lambda](https://github.com/code-423n4/2023-01-tessera-mitigation-findings/issues/10).
