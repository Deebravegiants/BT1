# [M] Revisited nonce Management in submit()

## Summary
Severity: Medium
Contest weight: 0.4592
Dataset id: 13146
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SwopX Lending protocol allows members to collateralize their NFTs and access short and long term liquidity from lenders. The borrowers start a loan when they submit a deal. While reviewing the loan submission logic, we notice the current nonce management needs to be revisited. To elaborate, we show below the related submit() function. It implements a rather straightforward logic in validating the given arguments and then starting a new loan. However, it comes to our attention the validation of given lenderSignature and borrowerSignature requires the freshness of lenderNonce and borrowerNonce. However, the current implementation does not mark both nonces used after the validation, which violates the freshness requirement.
```solidity
function submit(uint256[2] calldata nonces, address _paymentAddress, address _lender, address _nftcontract, uint256 _nftTokenId, uint256[3] calldata _loanAmounLoanCost, uint256 _offeredTime, bytes32 _gist, bytes calldata borrowerSignature, bytes calldata lenderSignature) 
    external 
    whenNotPaused 
    nonReentrant 
    supportInterface(_paymentAddress)
{
    LendingAssets memory _m = LendingAssets({
        paymentContract: address(_paymentAddress),
        listingTime: clockTimeStamp(),
        totalPrincipal: _loanAmounLoanCost[0],
        totalInterest: _loanAmounLoanCost[1],
        totalInterestPaid: 0,
        totalAmountLoan: _loanAmounLoanCost[0] + _loanAmounLoanCost[1],
        totalAmountPaid: 0,
        termId: 1,
        isPaid: false,
        borrowerNonce: nonces[0],
        lenderNonce: nonces[1],
        nftcontract: _nftcontract,
        nftTokenId: _nftTokenId,
        gist: _gist
    });
    require(IERC721(_m.nftcontract).ownerOf(_m.nftTokenId) == msg.sender, "Not NFT Owner");
    require(identifiedSignature[_lender][_m.lenderNonce] != true, "Lender is not interested");
    require(_offeredTime >= clockTimeStamp(), "offer expired");
    require(IERC20(_m.paymentContract).allowance(_lender, receiverAddress) >= _m.totalPrincipal, "Not enough allowance");
    require(_loanAmounLoanCost[2] >= calculatedFee(_m.totalPrincipal), "fee");
    require(_verify(_lender, _hashLending(_m.lenderNonce, _m.paymentContract, _offeredTime, _m.totalPrincipal, _m.totalInterest, _m.nftcontract, msg.sender, _m.nftTokenId, _m.gist), lenderSignature), "Invalid lender signature");
    require(_verify(msg.sender, _hashBorrower(_m.borrowerNonce, _m.nftcontract, _m.nftTokenId, _m.gist), borrowerSignature), "Invalid borrower signature");
    uint256 counterId = counter();
    _assets[counterId] = _m;
    _receipt[counterId].lenderToken = nftCounter();
    _receipt[counterId].borrowerToken = nftCounter();
    Receipt memory _nft = _receipt[counterId];
    _mint(_lender, _nft.lenderToken);
    _setTokenURI(_nft.lenderToken, string(abi.encodePacked(Strings.toString(_nft.lenderToken), ".json")));
    _mint(msg.sender, _nft.borrowerToken);
    _setTokenURI(_nft.borrowerToken, string(abi.encodePacked(Strings.toString(_nft.borrowerToken), ".json")));
}
```

## Recommendation
Properly mark the nonces as used to ensure their freshness.
