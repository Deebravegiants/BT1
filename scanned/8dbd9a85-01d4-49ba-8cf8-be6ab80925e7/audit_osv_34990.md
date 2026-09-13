# [H] CVE-2025-67172

## Summary
Severity: High
Advisory: CVE-2025-67172
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-67172
Type: osv

## Details
RiteCMS v3.1.0 was discovered to contain an authenticated remote code execution (RCE) vulnerability via the parse_special_tags() function.

## References
- https://github.com/handylulu/RiteCMS/
- https://github.com/handylulu/RiteCMS/blob/master/cms/includes/functions.inc.php#L297
- https://github.com/handylulu/RiteCMS/blob/master/cms/includes/functions.inc.php#L504
- https://github.com/mbiesiad/vulnerability-research/tree/main/CVE-2025-67172
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67172.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67172
