# [C] CVE-2024-46506

## Summary
Severity: Critical
Advisory: CVE-2024-46506
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-05-13
Source: https://osv.dev/vulnerability/CVE-2024-46506
Type: osv

## Details
NetAlertX 23.01.14 through 24.x before 24.10.12 allows unauthenticated command injection via settings update because function=savesettings lacks an authentication requirement, as exploited in the wild in May 2025. This is related to settings.php and util.php.

## References
- https://rhinosecuritylabs.com/research/cve-2024-46506-rce-in-netalertx/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46506.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46506
