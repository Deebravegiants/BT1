# [H] XXL-JOB vulnerable to Server-Side Request Forgery

## Summary
Severity: High
Advisory: GHSA-c352-x843-ggpq
CVE: CVE-2024-24113
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-08
Source: https://github.com/advisories/GHSA-c352-x843-ggpq
Type: github-advisory

## Affected
- Maven: `com.xuxueli:xxl-job` — affected >=0

## Details
xxl-job <= 2.4.2 has a Server-Side Request Forgery (SSRF) vulnerability, which causes low-privileged users to control executor to RCE.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24113
- https://github.com/xuxueli/xxl-job/issues/3375
- https://github.com/xuxueli/xxl-job
