# [C] PutongOJ: unprivileged users can escalate privileges by constructing requests

## Summary
Severity: Critical
Advisory: CVE-2024-48920
Aliases: GHSA-gj6h-73c5-xw6f
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-10-17
Source: https://osv.dev/vulnerability/CVE-2024-48920
Type: osv

## Details
PutongOJ is online judging software. Prior to version 2.1.0-beta.1, unprivileged users can escalate privileges by constructing requests. This can lead to unauthorized access, enabling users to perform admin-level operations, potentially compromising sensitive data and system integrity. This problem has been fixed in v2.1.0.beta.1. As a workaround, one may apply the patch from commit `211dfe9` manually.

## References
- https://github.com/acm309/PutongOJ/releases/tag/v2.1.0-beta.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48920.json
- https://github.com/acm309/PutongOJ/security/advisories/GHSA-gj6h-73c5-xw6f
- https://nvd.nist.gov/vuln/detail/CVE-2024-48920
- https://github.com/acm309/PutongOJ/commit/211dfe9ebf1c6618ce5396b0338de4f9b580715e#diff-782628b47d666d5d551e040815ca3f80c0704397258718f0e0f31164608ea7beL118-R120
