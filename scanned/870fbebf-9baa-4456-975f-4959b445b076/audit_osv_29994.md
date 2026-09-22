# [H] CVE-2024-48766

## Summary
Severity: High
Advisory: CVE-2024-48766
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-05-13
Source: https://osv.dev/vulnerability/CVE-2024-48766
Type: osv

## Details
NetAlertX 24.7.18 before 24.10.12 allows unauthenticated file reading because an HTTP client can ignore a redirect, and because of factors related to strpos and directory traversal, as exploited in the wild in May 2025. This is related to components/logs.php.

## References
- https://raw.githubusercontent.com/rapid7/metasploit-framework/master/modules/auxiliary/scanner/http/netalertx_file_read.rb
- https://rhinosecuritylabs.com/research/cve-2024-46506-rce-in-netalertx/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48766.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48766
