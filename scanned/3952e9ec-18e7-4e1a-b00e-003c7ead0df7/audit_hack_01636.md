# [M] TBTC incident: After about 48 hours of testing on both the Ethereum and Bitcoin mainnets, the Keep team decided to trigger the 10-day emergency d

## Summary
Severity: Medium
Target: TBTC
Loss: -
Attack method: Insufficient testing
Published: 2020-05-18
Source: https://www.8btc.com/article/599249
Type: slowmist-incident

## Details
After about 48 hours of testing on both the Ethereum and Bitcoin mainnets, the Keep team decided to trigger the 10-day emergency deposit moratorium allowed by the TBTCSystem contract, the team found that deposits were being blocked when certain types of Bitcoin addresses were used for redemption. The decision to trigger the moratorium came after a major issue with the redemption flow of the contract that put open deposit signer deposits at risk of liquidation. The team summarizes as follows: 1. First, the Keep team failed to conduct more tests after the new commit was proposed. As a result, the team missed the opportunity to catch this issue during development. 2. During the dApp-based manual QA process, the Keep team did not verify whether a successful exchange in the UI resulted in a closed deposit on-chain. As a result, the team missed the opportunity to find issues during the manual QA process. 3. The Keep team did not adequately consider input validation at the entry point of redemption. This is one of the relatively few pieces of data in the system that is completely user-controlled, and should therefore be a top consideration for input validation. 4. The Keep team did not spend enough time generating Bitcoin test vectors for unit tests.
