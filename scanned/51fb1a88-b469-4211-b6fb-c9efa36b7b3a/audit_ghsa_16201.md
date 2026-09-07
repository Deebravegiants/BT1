# [M] m2crypto Bleichenbacher timing attack - incomplete fix for CVE-2020-25657

## Summary
Severity: Medium
Advisory: GHSA-944j-8ch6-rf6x
CVE: CVE-2023-50781
CWE: CWE-203, CWE-208, CWE-385
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-05
Source: https://github.com/advisories/GHSA-944j-8ch6-rf6x
Type: github-advisory

## Affected
- PyPI: `m2crypto` — affected >=0

## Details
A flaw was found in m2crypto. This issue may allow a remote attacker to decrypt captured messages in TLS servers that use RSA key exchanges, which may lead to exposure of confidential or sensitive data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50781
- https://access.redhat.com/security/cve/CVE-2023-50781
- https://bugzilla.redhat.com/show_bug.cgi?id=2254426
- https://gitlab.com/m2crypto/m2crypto
- https://gitlab.com/m2crypto/m2crypto/-/issues/342
