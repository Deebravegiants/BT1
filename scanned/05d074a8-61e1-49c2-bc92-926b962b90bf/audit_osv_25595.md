# [C] uthenticode signature validation bypass vulnerability

## Summary
Severity: Critical
Advisory: CVE-2023-39969
Aliases: GHSA-rc7g-99x7-4p9g
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-08-09
Source: https://osv.dev/vulnerability/CVE-2023-39969
Type: osv

## Details
uthenticode is a small cross-platform library for partially verifying Authenticode digital signatures. Version 1.0.9 of uthenticode hashed the entire file rather than hashing sections by virtual address, in violation of the Authenticode specification. As a result, an attacker could modify code within a binary without changing its Authenticode hash, making it appear valid from uthenticode's perspective. Versions of uthenticode prior to 1.0.9 are not vulnerable to this attack, nor are versions in the 2.x series. By design, uthenticode does not perform full-chain validation. However, the malleability of signature verification introduced in 1.0.9 was an unintended oversight. The 2.x series addresses the vulnerability. Versions prior to 1.0.9 are also not vulnerable, but users are encouraged to upgrade rather than downgrade. There are no workarounds to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39969.json
- https://github.com/trailofbits/uthenticode/security/advisories/GHSA-rc7g-99x7-4p9g
- https://nvd.nist.gov/vuln/detail/CVE-2023-39969
- https://github.com/trailofbits/uthenticode/commit/8670b7bb9154d79c276483dcb7c9e9fd5e66455b
- https://github.com/trailofbits/uthenticode/pull/84
