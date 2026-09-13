# [C] XXL-JOB contains a Command execution vulnerability in background tasks 

## Summary
Severity: Critical
Advisory: GHSA-m54f-rp6r-rrrm
CVE: CVE-2022-40929
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-29
Source: https://github.com/advisories/GHSA-m54f-rp6r-rrrm
Type: github-advisory

## Affected
- Maven: `com.xuxueli:xxl-job-core` — affected >=0

## Details
XXL-JOB versions 2.2.0 and prior contain a Command execution vulnerability in background tasks.

NOTE: this is disputed because the issues/4929 report is about an intended and supported use case (running arbitrary Bash scripts on behalf of users).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40929
- https://github.com/xuxueli/xxl-job/issues/2979
- https://github.com/xuxueli/xxl-job
