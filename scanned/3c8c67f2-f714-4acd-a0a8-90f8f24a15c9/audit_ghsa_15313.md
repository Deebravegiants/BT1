# [H] Improper Preservation of Permissions in xxl-job

## Summary
Severity: High
Advisory: GHSA-cpfp-m5qw-c4r3
CVE: CVE-2024-42681
CWE: CWE-276, CWE-277, CWE-281
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-15
Source: https://github.com/advisories/GHSA-cpfp-m5qw-c4r3
Type: github-advisory

## Affected
- Maven: `com.xuxueli:xxl-job-core` — affected >=0 <2.4.2

## Details
Insecure Permissions vulnerability in xxl-job v.2.4.1 allows a remote attacker to execute arbitrary code via the Sub-Task ID component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-42681
- https://github.com/xuxueli/xxl-job/issues/3516
- https://github.com/xuxueli/xxl-job/commit/a2dc9011310628f3e18c3a5095e7e6a946d017bd
- https://github.com/xuxueli/xxl-job
