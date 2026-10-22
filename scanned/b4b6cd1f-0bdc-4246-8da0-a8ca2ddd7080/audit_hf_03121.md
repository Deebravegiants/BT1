# [H] ERC4626Oracle Price will be wrong when the

## Summary
Severity: High
Contest weight: 0.5929
Dataset id: 17601
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
EIP-4626 does not require the decimals must be the same as the underlying tokens' decimals, and when it's not, ERC4626Oracle will malfunction.
In the current implementation, IERC4626(token).decimals() is used as the IERC4626(token).asset()'s decimals to calculate the ERC4626's price.
However, while most ERC4626s are using the underlying token’s decimals as decimals, there are some ERC4626s use a different decimals from underlying token’s decimals since EIP-4626 does not require the decimals must be the same as the underlying token’s decimals:
Although the convertTo functions should eliminate the need for any use of an EIP-4626 Vault’s decimals variable, it is still strongly recommended to mirror the underlying token’s decimals if at all possible, to eliminate possible sources of confusion and simplify integration across front-ends and for other off-chain users.
Ref: https://eips.ethereum.org/EIPS/eip-4626
The price of ERC4626 will be significantly underestimated when the underlying token's decimals > ERC4626's decimals, and be significantly overestimated when the underlying token's decimals < ERC4626's decimals.

## Recommendation
getPrice() can be changed to:
```solidity
function getPrice(address token) external view returns (uint) {
    uint decimals = IERC4626(token).decimals();
    address underlyingToken = IERC4626(token).asset();
    return IERC4626(token).previewRedeem(
        10 ** decimals
    ).mulDivDown(
        oracleFacade.getPrice(underlyingToken),
        10 ** IERC20Metadata(underlyingToken).decimals()
    );
}
```
Confirmed fix.
