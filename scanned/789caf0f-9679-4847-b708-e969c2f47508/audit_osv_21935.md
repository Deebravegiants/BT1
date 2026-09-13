# [C] Command Injection Vulnerability in hestiacp/hestiacp

## Summary
Severity: Critical
Advisory: CVE-2022-1509
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-04-28
Source: https://osv.dev/vulnerability/CVE-2022-1509
Type: osv

## Details
Command Injection Vulnerability in GitHub repository hestiacp/hestiacp prior to 1.5.12. An authenticated remote attacker with low privileges can execute arbitrary code under root context.

## References
- https://huntr.dev/bounties/09e69dff-f281-4e51-8312-ed7ab7606338
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1509.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1509
- https://github.com/hestiacp/hestiacp/commit/d50f95cf208049dfb6ac67a8020802121745bd60
