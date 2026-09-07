# [M] `indexed` Keyword in Events Causes Data Loss for Dynamic Array Variables

## Summary
Severity: Medium
Chain: Smart contract
Component: Tapioca--Lending-Engine-
Published: 2024-06-07
Source: https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/issues/27
Type: hats-finding

## Details
**Github username:** @MatinR1
**Twitter username:** MatinRezaii1
**Submission hash (on-chain):** 0xa5d3c41c908b75f7ae9a660281a4330a0e74ed0e31bef7ffebb42e3671eb5961
**Severity:** medium

**Description:**
**Description**\
when the `indexed` keyword is used for reference type variables such as dynamic arrays or strings, it will return the hash of the mentioned variables. 
Thus, the event which is supposed to inform all of the applications subscribed to its emitting transaction (e.g. front-end of the DApp, or the backend listeners to that event), would get a meaningless and obscure 32 bytes that correspond to keccak256 of an encoded string. This may cause some problems on the DApp side and even lead to data loss. For more information about the indexed events, check here:

(https://docs.soliditylang.org/en/v0.8.17/abi-spec.html?highlight=indexed#events)

The problem exists inside the `Penrose` contract. The event `ProtocolWithdrawal` is defined in such a way that the dynamical array of IMarkets is indexed. With doing so, the expected parameters wouldn't be emitted properly and front-end would get meaningless one-way hashes.

**Attachments**

1. **Proof of Concept (PoC) File**

Consider this scenario as an example:

1 - The function `withdrawAllMarketFees()` is called by the owner

2 - Inside the function `withdrawAllMarketFees()` we expect to see the the array of "IMarkets":

```
    function withdrawAllMarketFees(IMarket[] calldata markets_, ITwTap twTap) external onlyOwner notPaused {
        if (address(twTap) == address(0)) revert ZeroAddress();

        uint256 length = markets_.length;
        unchecked {
            for (uint256 i; i < length;) {
                _depositFeesToTwTap(markets_[i], twTap);
                ++i;
            }
        }

        emit ProtocolWithdrawal(markets_, block.timestamp);
    }
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/issues/27_
