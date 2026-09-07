# [M] Loan offer's required collateral tokenId is not validated in some conditions, borrower can use any NFT to initiate loans

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-05-gondi-mitigation
Published: 2024-05-24
Source: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/119
Type: code-finding

## Details
# Lines of code

https://github.com/pixeldaogg/florida-contracts/blob/7bacbe3f2b4c1bb6c87961e3553118a6e6c2dcee/src/lib/loans/MultiSourceLoan.sol#L850


# Vulnerability details

### Impacts
Loan offer's required collateral tokenId is not validated in some conditions, borrower can use any NFT to initiate loans.

### Proof of concept
When a lender generate LoanOffer, they can either specify a specific NFT tokenId, or allow a collection offer (any tokenId within the NFT collection). LoanOffer and executionData's collateral Id match is checked in `_checkValidators()`.

Based on code doc, a lender's LoanOffer struct -> the collateral tokenId required :
(1) Empty validator array input -> lender want the exact tokenId match;
(2) Single validator element input && _loanOffer.validators[0].validator == address(0) -> lender accepts any token in the collection;
(3) Non-empty validator array &&_loanOffer.validators[0].validator != address(0) -> lender wants offer validators to check the offer.
```solidity
|>  /// @notice Check generic offer validators for a given offer or
    ///         an exact match if no validators are given. The validators
    ///         check is performed only if tokenId is set to 0.
    ///         Having one empty validator is used for collection offers (all IDs match).
...
    function _checkValidators(LoanOffer calldata _loanOffer, uint256 _tokenId) private view {
...
```
Edge case: A lender wants an exact tokenId match and the tokenId is 0. 

Based on the code doc, an exact match check should be performed when no validators are given. So lender's LoanOffer will be: (1) _loanOffer.nftCollateralTokenId =0 ; (2) _loanOffer.validators.length == 0;

However, _checkValidators() will not check this loanOffer at all. Due to empty validator array is provided, exact tokenId match is not checked due to vulnerable check `if (_loanOffer.nftCollateralTokenId != 0){...`. In the else branch, for-loop will be directly skipped, and exit the function with no checks.
```solidity
    function _checkValidators(LoanOffer calldata _loanOffer, uint256 _tokenId) private view {
       uint256 offerTokenId = _loanOffer.nftCollateralTokenId;
        //@audit This is vulnerable check condition, will cause tokenId=0 and empty validators to be skipped entirely
 |>     if (_loanOffer.nftCollateralTokenId != 0) {
            if (offerTokenId != _tokenId) {
                revert InvalidCollateralIdError();
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/119_
