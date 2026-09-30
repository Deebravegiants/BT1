# [M] MOKE incident: The MOKE token protocol on BNB Chain was exploited via a smart contract vulnerability. The attacker abused an unprotected public c

## Summary
Severity: Medium
Target: MOKE
Loss: $ 907700
Attack method: Smart Contract Vulnerability
Published: 2026-08-02
Source: https://x.com/TenArmorAlert/status/2084102947500368164
Type: slowmist-incident

## Details
The MOKE token protocol on BNB Chain was exploited via a smart contract vulnerability. The attacker abused an unprotected public claim() function in MokeToken.releaseContract() (no eligibility check on the caller), repeatedly draining ~166 million MOKE from the protocol’s internal reserve pool, then used flash loans, Venus leverage, LP removal, and dividend distribution mechanisms to convert it into ~1,546 BNB, resulting in a loss of approximately $907,700.
