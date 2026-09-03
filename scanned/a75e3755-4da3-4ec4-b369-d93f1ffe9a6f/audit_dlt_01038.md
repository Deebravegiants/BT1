# [M] IO FinNet tss-lib vulnerable to replay attacks involving proofs

## Summary
Severity: Medium
Chain: github.com/bnb-chain/tss-lib
Component: github.com/bnb-chain/tss-lib, github.com/binance-chain/tss-lib
CVE: CVE-2022-47930
CWE: Authentication Bypass by Capture-replay
Published: 2023-04-21
Source: https://github.com/advisories/GHSA-c58h-qv6g-fw74
Type: github-advisory

## Details
An issue was discovered in IO FinNet tss-lib before 2.0.0. The parameter ssid for defining a session id is not used through the MPC implementation, which makes replaying and spoofing of messages easier. In particular, the Schnorr proof of knowledge implemented in sch.go does not utilize a session id, context, or random nonce in the generation of the challenge. This could allow a malicious user or an eavesdropper to replay a valid proof sent in the past.
