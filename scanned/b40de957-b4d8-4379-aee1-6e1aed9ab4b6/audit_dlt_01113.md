# [M] Utils.readChallengeTx does not verify the server account signature

## Summary
Severity: Medium
Chain: stellar-sdk
Component: stellar-sdk
CVE: CVE-2021-32738
CWE: Improper Authentication, Improper Verification of Cryptographic Signature
Published: 2021-07-02
Source: https://github.com/advisories/GHSA-6cgh-hjpw-q3gq
Type: github-advisory

## Details
The `Utils.readChallengeTx` function used in [SEP-10 Stellar Web Authentication](https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0010.md) states in its function documentation that it reads and validates the challenge transaction including verifying that the `serverAccountID` has signed the transaction. The function does not verify that the server has signed the transaction and has been fixed so that it does in v8.2.3.

Applications that also used `Utils.verifyChallengeTxThreshold` or `Utils.verifyChallengeTxSigners` to verify the signatures including the server signature on the challenge transaction are unaffected as those functions verify the server signed the transaction.

Applications calling `Utils.readChallengeTx` should update to v8.2.3 to ensure that the challenge transaction is completely valid and signed by the server creating the challenge transaction.
