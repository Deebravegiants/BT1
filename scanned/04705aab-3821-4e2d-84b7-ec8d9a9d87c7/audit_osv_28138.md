# [H] OS Command Injection Vulnerability in SOY CMS

## Summary
Severity: High
Advisory: CVE-2024-28187
Aliases: GHSA-qg3q-hfgc-5jmm
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-11
Source: https://osv.dev/vulnerability/CVE-2024-28187
Type: osv

## Details
SOY CMS is an open source CMS (content management system) that allows you to build blogs and online shops. SOY CMS versions prior to 3.14.2 are vulnerable to an OS Command Injection vulnerability within the file upload feature when accessed by an administrator. The vulnerability enables the execution of arbitrary OS commands through specially crafted file names containing a semicolon, affecting the jpegoptim functionality. This vulnerability has been patched in version 3.14.2. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28187.json
- https://github.com/inunosinsi/soycms/security/advisories/GHSA-qg3q-hfgc-5jmm
- https://nvd.nist.gov/vuln/detail/CVE-2024-28187
- https://github.com/inunosinsi/soycms/commit/9b0e452f628df28dec69cd72b6b55db21066cbf8
