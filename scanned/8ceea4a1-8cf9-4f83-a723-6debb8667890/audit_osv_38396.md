# [H] osslsigncode has a Stack Buffer Overflow via Unbounded Digest Copy During Signature Verification

## Summary
Severity: High
Advisory: CVE-2026-39853
Aliases: GHSA-hx87-8754-xvh4
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-39853
Type: osv

## Details
osslsigncode is a tool that implements Authenticode signing and timestamping. Prior to 2.12, A stack buffer overflow vulnerability exists in osslsigncode in several signature verification paths. During verification of a PKCS#7 signature, the code copies the digest value from a parsed SpcIndirectDataContent structure into a fixed-size stack buffer  (mdbuf[EVP_MAX_MD_SIZE], 64 bytes) without validating that the source length fits within the destination buffer. This pattern is present in the verification handlers for PE, MSI, CAB, and script files. An attacker can craft a malicious signed file with an oversized digest field in SpcIndirectDataContent. When a user verifies such a file with osslsigncode verify, the unbounded memcpy can overflow the stack buffer and corrupt adjacent stack state. This vulnerability is fixed in 2.12.

## References
- https://github.com/mtrojnar/osslsigncode/releases/tag/2.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39853.json
- https://github.com/mtrojnar/osslsigncode/security/advisories/GHSA-hx87-8754-xvh4
- https://nvd.nist.gov/vuln/detail/CVE-2026-39853
- https://github.com/mtrojnar/osslsigncode/commit/cbee1e723c5a8547302bd841ad9943ed8144db68
