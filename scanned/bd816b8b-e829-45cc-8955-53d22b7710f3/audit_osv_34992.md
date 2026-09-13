# [M] CVE-2025-67174

## Summary
Severity: Medium
Advisory: CVE-2025-67174
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-67174
Type: osv

## Details
A local file inclusion (LFI) vulnerability in RiteCMS v3.1.0 allows attackers to read arbitrary files on the host via a directory traversal in the admin_language_file and default_page_language_file in the admin.php component

## References
- https://github.com/handylulu/RiteCMS/blob/master/admin.php#L46
- https://github.com/handylulu/RiteCMS/blob/master/cms/subtemplates/settings.inc.tpl#L64
- https://github.com/mbiesiad/vulnerability-research/tree/main/CVE-2025-67174
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67174.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67174
- https://github.com/handylulu/RiteCMS
