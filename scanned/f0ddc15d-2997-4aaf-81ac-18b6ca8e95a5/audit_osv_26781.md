# [M] Bludit 3.13.1 Authenticated Arbitrary File Download via Backup Plugin

## Summary
Severity: Medium
Advisory: CVE-2023-53907
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2023-53907
Type: osv

## Details
Bludit versions before 3.13.1 contain an authenticated file download vulnerability in the Backup Plugin that allows logged-in users to access arbitrary files. Attackers can exploit the plugin's download functionality by manipulating file path parameters to read sensitive system files through directory traversal.

## References
- https://www.bludit.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53907.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53907
- https://www.vulncheck.com/advisories/bludit-authenticated-arbitrary-file-download-via-backup-plugin
- https://www.exploit-db.com/exploits/51541
