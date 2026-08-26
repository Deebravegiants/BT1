# [M] Vault fees can be set to anything when initilizing

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-01-popcorn
Published: 2023-02-07
Source: https://github.com/code-423n4/2023-01-popcorn-findings/issues/396
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-01-popcorn/blob/d95fc31449c260901811196d617366d6352258cd/src/vault/Vault.sol#L57


# Vulnerability details

## Impact
The vault owner can charge any fees when initializing. Because of this a lot of problems can occur
1. If the fees are set at 1e18, the withdraw function won't work as it will cause division by 0 error.
2. If all the fees are set beyond 1e18, many of the functions won't work due to arithmetic overflow.

## Proof of Concept
Below is the code where the fees can be set to anything during the initialization
```
function initialize(
        IERC20 asset_,
        IERC4626 adapter_,
        VaultFees calldata fees_,
        address feeRecipient_,
        address owner
    ) external initializer {
       //code
        fees = fees_;
      // code
```
Here is a test to confirm the same
```
function test_Vault_any_Fees() public{
    address vaultAddress1 = address(new Vault());
    Vault vault1;
    vault1 = Vault(vaultAddress1);
    vault1.initialize(
      IERC20(address(asset)),
      IERC4626(address(adapter)),
      VaultFees({ deposit: 2e18, withdrawal: 2e18, management: 2e18, performance: 2e18 }),
      feeRecipient,
      address(this)
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-01-popcorn-findings/issues/396_
