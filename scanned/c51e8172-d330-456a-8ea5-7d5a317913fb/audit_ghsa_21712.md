# [H] Zip slip in Microweber

## Summary
Severity: High
Advisory: GHSA-pqcf-v8v5-jmcg
CVE: CVE-2020-28337
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-pqcf-v8v5-jmcg
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.2.3

## Details
A directory traversal issue in the Utils/Unzip module in Microweber through 1.1.20 allows an authenticated attacker to gain remote code execution via the backup restore feature. To exploit the vulnerability, an attacker must have the credentials of an administrative user, upload a maliciously constructed ZIP file with file paths including relative paths (i.e., ../../), move this file into the backup directory, and execute a restore on this file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28337
- https://github.com/microweber/microweber/commit/777ee9c3e7519eb3672c79ac41066175b2001b50
- https://sl1nki.page/advisories/CVE-2020-28337
- https://sl1nki.page/blog/2021/02/01/microweber-zip-slip
- http://packetstormsecurity.com/files/162514/Microweber-CMS-1.1.20-Remote-Code-Execution.html
