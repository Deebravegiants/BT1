# [M] Rounding in LovTokenManager doesn't sync with design

## Summary
Severity: Medium
Chain: Smart contract
Component: Origami
Published: 2024-02-25
Source: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/32
Type: hats-finding

## Details
**Github username:** @Tri-pathi
**Twitter username:** 0xTripathi
**Submission hash (on-chain):** 0x1b2d808d59af662b3aa9facc49704b0282012c0ec61d4cddeb99e5ebba64f294
**Severity:** medium

**Description:**
**Description**

In the LovTokenManager, the rounding behavior deviates from the intended design. According to the protocol, values should be rounded down, but this is not consistently implemented.

**Attack Scenario**



**Attachments**

1. **Proof of Concept (PoC) File**

The `OrigamiAbstractLovTokenManager::_reservesToShares()` function is pivotal for determining the number of lovTokens a user receives for a given amount of reserve tokens and the current lovToken totalSupply.

According to the protocol's design, this amount should be rounded down. However, the current implementation fails to adhere to this rule.

```solidity
File: apps/protocol/contracts/investments/lovToken/managers/OrigamiAbstractLovTokenManager.sol

    function _reservesToShares(Cache memory cache, uint256 reserves) private view returns (uint256) {
        // If totalSupply is zero, then just return reserves 1:1 scaled up to the shares decimals
        // If > 0 then the decimal conversion is handled already (numerator cancels out denominator)
        if (cache.totalSupply == 0) {
            return reserves.scaleUp(_reservesToSharesScalar());
        }

        // In the unlikely case that no available reserves for user withdrawals (100% of reserves are held back to repay debt),
        // then revert
        uint256 _redeemableReserves = _userRedeemableReserves(cache);

        if (_redeemableReserves == 0) {
            revert NoAvailableReserves();
        }

        // Round down for calculating shares from reserves
        return reserves.mulDiv(cache.totalSupply, _redeemableReserves, OrigamiMath.Rounding.ROUND_DOWN);

        // (reserves*totalSupply)/_redeemableReserves total round down
    }
```
https://github.com/TempleDAO/origami-public/blob/main/apps/protocol/contracts/investments/lovToken/managers/OrigamiAbstractLovTokenManager.sol#L642

if lovToken's total supply is zero then it just return reserves 1:1 scaled uo to the shares decimals. 

else

first it calculates available reserves for user withdrawl from `_userRedeemableReserves(cache)`

```solidity
File: apps/protocol/contracts/investments/lovToken/managers/OrigamiAbstractLovTokenManager.sol

    function _userRedeemableReserves(Cache memory cache) internal view returns (uint256) {
        // Round up for liabilities with buffer
        uint256 _bufferBps = redeemableReservesBufferBps;
        uint256 _liabilitiesWithBuffer = _bufferBps == OrigamiMath.BASIS_POINTS_DIVISOR
            ? cache.liabilities
            : cache.liabilities.mulDiv(
                _bufferBps, 
                OrigamiMath.BASIS_POINTS_DIVISOR,
                OrigamiMath.Rounding.ROUND_UP
            );

        unchecked {
            return cache.assets > _liabilitiesWithBuffer
                ? cache.assets - _liabilitiesWithBuffer
                : 0;
        }
    }
```
https://github.com/TempleDAO/origami-public/blob/main/apps/protocol/contracts/investments/lovToken/managers/OrigamiAbstractLovTokenManager.sol#L603


As we can see `_liabilitiesWithBuffer` is `ROUND_UP` and this function returns `cache.assets - _liabilitiesWithBuffer` which can be taken overall `ROUND_DOWN` , making `_redeemableReserves` round down.

Formula of calculating shares is (reserves * totalSupply )/ _redeemableReserves which should be overall rounddown but as `_redeemableReserves ` is already round down makes this expression round up which is exactly opposite to the design. 

Hence it can end up being roundup instead of rounddown




2. **Revised Code File (Optional)**

Ensure all the transfer assets/tokens to user are rounded down properly
