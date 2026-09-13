# [C] Concrete CMS Vulnerable to Relative Path Traversal

## Summary
Severity: Critical
Advisory: GHSA-645j-cm4x-3xvw
CVE: CVE-2026-8134
CWE: CWE-23
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-645j-cm4x-3xvw
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below fails to sanitize path traversal sequences in the ptComposerFormLayoutSetControlCustomTemplate field when saving page type composer form layouts. An authenticated rogue administrator with composer form editing rights can exploit this to include arbitrary readable files on the server. Combined with the file uploader's extension-only validation (which permits PHP code in files saved with image extensions like .png), this can result in authenticated remote code execution. Concrete CMS thanks Yonatan Drori (Tenzai) for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8134
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
