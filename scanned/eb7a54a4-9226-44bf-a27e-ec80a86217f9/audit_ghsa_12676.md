# [H] mx-chain-go does not treat invalid transaction with wrong username correctly

## Summary
Severity: High
Advisory: GHSA-7xpv-4pm9-xch2
CVE: CVE-2023-33964
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2023-06-02
Source: https://github.com/advisories/GHSA-7xpv-4pm9-xch2
Type: github-advisory

## Affected
- Go: `github.com/multiversx/mx-chain-go` — affected >=0 <1.4.16

## Details
### Impact
Metachain cannot process a cross-shard miniblock.
An invalid transaction with the wrong username on metachain is not treated correctly on the metachain transaction processor. This is strictly a processing issue that could have happened on MultiversX chain. If an error like this had occurred, the metachain would have stopped notarizing blocks from the shard chains. The resuming of notarization is possible only after applying a patched binary version. 
 
### Patches
Introduce processIfTxErrorCrossShard for metachain transaction processor. 

### Workarounds
No

### References
No

## References
- https://github.com/multiversx/mx-chain-go/security/advisories/GHSA-7xpv-4pm9-xch2
- https://nvd.nist.gov/vuln/detail/CVE-2023-33964
- https://github.com/multiversx/mx-chain-go/commit/97295471465f4b5f79e51b32f8b7111f8d921606
- https://github.com/multiversx/mx-chain-go
