# [M] wrong implementation of mint function

## Summary
Severity: Medium
Reporter: Puny Fiery Alpaca
Source: https://github.com/sherlock-audit/2023-12-dodo-gsp/blob/main/dodo-gassaving-pool/contracts/GasSavingPool/impl/GSPFunding.sol#L79
Type: audit-issue

## Details
# wrong implementation of mint function

## Summary
Here we are using  _mint(to, shares);  but we are not verifying whether the address is zero or not
## Vulnerability Detail
 _mint(to, shares); Here there should be a verification of address 0. As all the shares will be minted to zero addresses.
## Impact
If we cannot use address 0 for 
## Code Snippet
https://github.com/sherlock-audit/2023-12-dodo-gsp/blob/main/dodo-gassaving-pool/contracts/GasSavingPool/impl/GSPFunding.sol#L79
## Tool used

Manual Review

## Recommendation
Use a zero address verification before minting the shares.
