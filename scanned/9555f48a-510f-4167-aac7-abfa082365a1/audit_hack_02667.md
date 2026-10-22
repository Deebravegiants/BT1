# [H] Either Pool.writeFrom or Pool.setDivestmentTimestamp can do nothing because Premia Pool does not implement both function in one pool, affecting VaultAdmin.sol#processAuction

## Summary
Severity: High
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L307-L323
Type: audit-issue

## Details
# Either Pool.writeFrom or Pool.setDivestmentTimestamp can do nothing because Premia Pool does not implement both function in one pool, affecting VaultAdmin.sol#processAuction

## Summary

Either Pool.writeFrom or Pool.setDivestmentTimestamp can do nothing because Premia Pool does not implement both function in one pool, affecting VaultAdmin.sol#processAuction

## Vulnerability Detail

In VaultAdmin.sol#processAuction, Pool.writeFrom and Pool.setDivestmentTimestamp is called if totalContractsSold > 0

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L307-L323

the issue is, according to the Pool implementation from Premia option, one pool does not implementation both writeFrom and setDivestmentTimestamp

the function setDivestmentTimestamp comes from the contract PoolIO.sol

https://github.com/Premian-Labs/premia-contracts/blob/933575896b4d862de83d2a0a8f9f164655dd2b80/contracts/pool/PoolIO.sol#L48

```solidity
    function setDivestmentTimestamp(uint64 timestamp, bool isCallPool)
        external
    {
```

the function Pool.writeFrom comes from the contract PoolWrite.sol

https://github.com/Premian-Labs/premia-contracts/blob/933575896b4d862de83d2a0a8f9f164655dd2b80/contracts/pool/PoolWrite.sol#L150

```solidity
    function writeFrom(
        address underwriter,
        address longReceiver,
        uint64 maturity,
        int128 strike64x64,
        uint256 contractSize,
        bool isCall
    ) 
```

For this reason, etiher writeFrom or  setDivestmentTimestamp can do nothing because PoolWrite and PoolIO does not inherit each other.

Here is an example in production from Premia option.

https://etherscan.io/address/0xb7cd1bb23c69b6becdf5aa0fe17c444db67f5d93#writeProxyContract

this is pool address for 

"address":"0xb7cd1bb23c69b6becdf5aa0fe17c444db67f5d93",
"chainId":1,
"name":"YFI/DAI - CALL",
"pairName":"YFI/DAI"

as we can see in the writeProxyContract section, only setDivestmentTimestamp is available to call, but not writeFrom function.

another place that we interact with the premia pool is in the function _withdrawReservedLiqudity inside the Vault.sol

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L550-L555

the function Pool.write also exists in 

https://etherscan.io/address/0xb7cd1bb23c69b6becdf5aa0fe17c444db67f5d93#writeProxyContract

but not writeFrom, so PoolWrite and PoolIO is two contract.

## Impact

The impact is:

if writeFrom function do nothing,

the logic failed to underwrites the contracts sold during the auction, the pool will not sends the short tokens
to the vault, and failed to send long tokens to the auction contract

if setDivestmentTimestamp do nothing,

collateral locked in the Premia pool will not be locked, which is against the business requirement.

## Code Snippet

## Tool used

Manual Review

## Recommendation

We recommend the project take a close look at the implementation of the pool.

https://github.com/Premian-Labs/premia-contracts/tree/master/contracts/pool

The project can set two pool address in the storage layout, one refers to poolWrite, one refers to PoolIO, then both function can be calld.

```solidity
                PoolWrite.writeFrom(
                    address(this),
                    address(l.Auction),
                    lastOption.expiry,
                    lastOption.strike64x64,
                    totalContractsSold,
                    l.isCall
                );

                uint64 divestmentTimestamp = uint64(block.timestamp + 24 hours);
                PoolIO.setDivestmentTimestamp(divestmentTimestamp, l.isCall);
```

```solidity
 if (reservedLiquidity > 0) { 
     // remove reserved liquidity from the pool, if available 
     PoolIO.withdraw(reservedLiquidity, l.isCall); 
 } 
  
 emit ReservedLiquidityWithdrawn(l.epoch, reservedLiquidity); 
```
