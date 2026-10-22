# [C] An attacker can force 0 shares to be minted for a liquidity provider

## Summary
Severity: Critical
Contest weight: 0.3606
Dataset id: 7229
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If there are no outstanding long positions an attacker can frontrun a call to addLiquidity(...) and open a max possible short position such that z = 0. Then when the liquidity provider's call will go through the _updateLiquidity(_shareReservesDelta) will be a NOOP since z = 0 and the if block below would want to avoid the division by 0:
// below z = shareReserves = 0
uint256 shareReserves = _marketState.shareReserves;
if (_shareReservesDelta != 0 && shareReserves > 0) {
    int256 updatedShareReserves = int256(shareReserves) +
        _shareReservesDelta;
    _marketState.shareReserves = uint256(
        // NOTE: There is a 1 wei discrepancy in some of the
        // calculations which results in this clamping being required.
        updatedShareReserves >= 0 ? updatedShareReserves : int256(0)
    ).toUint128();
    _marketState.bondReserves = uint256(_marketState.bondReserves)
        .mulDivDown(_marketState.shareReserves, shareReserves)
        .toUint128();
}
And therefore the point (z, y) stays the same and does not get scaled. Thus endingPresentValue == startingPresentValue and so the lpShares calculated below would be 0:
lpShares = (endingPresentValue - startingPresentValue).mulDivDown(
    lpTotalSupply,
    startingPresentValue
);
now when _mint(...) is called with a 0 value as 'lpShares:
// Mint LP shares to the supplier.
_mint(AssetId._LP_ASSET_ID, _destination, lpShares);
The MultiToken's implementation of _mint(...) will be called:
function _mint(
    uint256 tokenID,
    address to,
    uint256 amount
) internal virtual {
    _balanceOf[tokenID][to] += amount;
    _totalSupply[tokenID] += amount;
    // Emit an event to track minting
    emit TransferSingle(msg.sender, address(0), to, tokenID, amount);
}
which allows minting when amount == 0.

## Recommendation
A simple fix would be to not allow MultiToken._mint(...) to mint when amount is equal to 0.
There is still an issue where lpShares would be really small due to the fact that the attacker can bring endingPresentValue really close to startingPresentValue. This still needs to be further analyzed.
