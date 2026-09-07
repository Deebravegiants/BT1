# [C] simogeo/filemanager arbitrary file upload vulnerability

## Summary
Severity: Critical
Advisory: GHSA-m5hw-rhvr-f47c
CVE: CVE-2025-46001
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-18
Source: https://github.com/advisories/GHSA-m5hw-rhvr-f47c
Type: github-advisory

## Affected
- Packagist: `simogeo/filemanager` — affected >=0

## Details
An arbitrary file upload vulnerability in the is_allowed_file_type() function of Filemanager v2.3.0 allows attackers to execute arbitrary code via uploading a crafted PHP file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-46001
- https://github.com/simogeo/Filemanager
- https://github.com/zakumini/CVE-List/blob/main/CVE-2025-46001/CVE-2025-46001.md
- https://www.exploit-db.com/exploits/38895
