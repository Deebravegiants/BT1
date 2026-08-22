# [M] MarketERC20::permit lacks of access control, enabling xChain calls relying on permits to be DoSed

## Summary
Severity: Medium
Chain: Smart contract
Component: Tapioca--Lending-Engine-
Published: 2024-06-03
Source: https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/issues/15
Type: hats-finding

## Details
**Github username:** @CergyK
**Twitter username:** --
**Submission hash (on-chain):** 0x154803094095bc5c6319f596cd6217ccd02f0d3b6a454c7e1f76624ebebdaf45
**Severity:** medium

**Description:**
**Description**
Any user can call `MarketERC20::permit` on behalf of an owner, 

**Attack Scenario**\
- Alice wants to do a cross-chain action, which needs a permit to be granted on the destination chain.
Alice initiates her action on mainnet, and provides permit data to be used on destination chain.

- Bob sees the action initiated by Alice on mainnet, and front-runs it by calling permit directly on destination chain, effectively DoSing the whole Alice xChain action.

**Recommendation**
Check that spender is msg.sender (or add a field `caller` to be checked on).

`contracts/market/MarketERC20.sol`:
```diff
function _permit(
    bool asset, // true = asset, false = collateral
    address owner,
    address spender,
    uint256 value,
    uint256 deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
) internal {
    require(block.timestamp <= deadline, "ERC20Permit: expired deadline");
+   require(msg.sender == spender, "not spender");

    bytes32 structHash;

    structHash = keccak256(
        abi.encode(
            asset ? _PERMIT_TYPEHASH : _PERMIT_TYPEHASH_BORROW, owner, spender, value, _useNonce(owner), deadline
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/issues/15_
