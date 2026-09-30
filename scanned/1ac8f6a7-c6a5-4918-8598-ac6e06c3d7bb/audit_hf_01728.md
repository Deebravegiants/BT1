# [C] Numerators are off by one

## Summary
Severity: Critical
Contest weight: 0.2787
Dataset id: 9436
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ClaimCore constructor will set the numerators ( numeratorUsdc, numeratorUsdt, numeratorNative ) for computing the required donation amount to claim the ZRO token.
However, the numerators are off by a factor of 10 as the base10 exponent is incorrectly subtracted by 1 during initialization. This will reduce the donations required by a factor of 10, allowing anyone to claim 10x more ZRO than expected.
```solidity
constructor(
    bytes32 _merkleRoot,
    address _donateContract,
    address _stargateUsdc,
    address _stargateUsdt,
    address _stargateNative,
    uint256 _nativePrice,
    address _owner
) Ownable(_owner) {
    merkleRoot = _merkleRoot;
    donateContract = IDonate(_donateContract);
    // TODO needs tests
    if (_stargateUsdc != address(0)) {
        // @audit this is off by a factor of 10
        numeratorUsdc = 1 * 10 ** (IERC20Metadata(IOFT(_stargateUsdc).token()).decimals() - 1);
    }
    if (_stargateUsdt != address(0)) {
        // @audit this is off by a factor of 10
        numeratorUsdt = 1 * 10 ** (IERC20Metadata(IOFT(_stargateUsdt).token()).decimals() - 1);
    }
    // native is always denominated in 18 decimals
    if (_stargateNative != address(0) && _nativePrice > 0) {
        // @audit this is off by a factor of 10
        numeratorNative = _nativePrice * 10 ** (18 - 1);
    }
    // Validate this is an actual native pool, eg. NOT WETH
    if (IOFT(_stargateNative).token() != address(0)) {
        revert InvalidNativeStargate();
    }
}
```

## Recommendation
Remove the subtraction by 1 in the initialization of numerators.
