# [H] Babylon Finality Provider `MsgCommitPubRandList` replay attack

## Summary
Severity: High
Advisory: GHSA-7mm3-vfg8-7rg6
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2025-05-15
Source: https://github.com/advisories/GHSA-7mm3-vfg8-7rg6
Type: github-advisory

## Affected
- Go: `github.com/babylonlabs-io/babylon` — affected >=0 <1.1.0

## Details
### Summary

A high vulnerability exists in the Babylon protocol's x/finality module due to a lack of domain separation in signed messages, combined with insufficient validation in the MsgCommitPubRandList handler. Specifically, the handler does not enforce that the submitted Commitment field is 32 bytes long. This allows an attacker to replay a signature originally generated for a different message (e.g., a Proof-of-Possession in MsgCreateFinalityProvider) as a MsgCommitPubRandList. By crafting the message parameters, an attacker can use the typically 20-byte address bytes (from the PoP context) to form the StartHeight, NumPubRand, and a shorter-than-expected Commitment (e.g., 4 bytes). The replayed signature will pass verification for this crafted message, leading to the injection of an invalid PubRand commitment.

### Impact

Successful exploitation of this vulnerability, specifically via the PoP signature replay, allows an attacker to store an invalid PubRand commitment (with a non-standard length, e.g., 4 bytes) for a targeted Finality Provider (FP). Despite the commitment itself being malformed, it's the associated StartHeight and NumPubRand (derived from the replayed address bytes and typically very large) that cause severe consequences

### Future recommendations

To minimize future risk of such attacks, all finality providers should:
1.  Never re-use your finality provider EOTS across the networks (e.g., the testnet) or for any other purpose. 
2. Never use EOTS keys to sign any other data than relevant to in-protocol messages. Ideally EOTS key should only be used to:
    - Sign initial proof of possession message
    - Sign periodic randomness commits
    - Sign finality votes with every block

### Finder
Vulnerability discovered by:
- Marco Hextor
- https://x.com/marcohextor
- @marcohextor

## References
- https://github.com/babylonlabs-io/babylon/security/advisories/GHSA-7mm3-vfg8-7rg6
- https://github.com/babylonlabs-io/babylon/commit/cb5d0ecae5cebc116d09296baaed25f715f904df
- https://github.com/babylonlabs-io/babylon
- https://pkg.go.dev/vuln/GO-2025-3686
