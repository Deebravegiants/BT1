# [C] Reserved assets could be extracted from the Vault

## Summary
Severity: Critical
Contest weight: 0.0000
Dataset id: 23337
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some strategy functions can release assets without checking if those assets are part of reservedLiquidity. AccountableFixedTerm._loan.drawableFunds is not verified to be in sync with the queue reservedLiquidity. Hence the borrower can inadvertently borrow more funds than they should.

## Proof of Concept
Violations occur in FixedTerm.acceptLoanLocked(), FixedTerm.borrow(), FixedTerm.pay(), FixedTerm.acceptLoanDynamic(), FixedTerm.claimInterest(): https://prover.certora.com/output/52567/edb399a43d1849a9b22f027e66b17924/?anonymousKey=3dcf62dfa004381083966b3639b6a485fa2e9501

```solidity
// Reserved liquidity must not exceed total assets
invariant reservedLiquidityBacked(env e)
ghostReservedLiquidity256 <= ghostTotalAssets256
```

## Recommendation
When reservedLiquidity is increased in the withdrawal queue, this needs to be synced to the FixedTerm starategy.
