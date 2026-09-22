# [M] OWASP CRS: Whitespace padding in filenames bypasses file upload extension checks

## Summary
Severity: Medium
Advisory: CVE-2026-33691
Aliases: GHSA-rw5f-9w43-gv2w
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-33691
Type: osv

## Details
The OWASP core rule set (CRS) is a set of generic attack detection rules for use with compatible web application firewalls. Prior to versions 3.3.9 and 4.25.0, a bypass was identified in OWASP CRS that allows uploading files with dangerous extensions (.php, .phar, .jsp, .jspx) by inserting whitespace padding in the filename (e.g. photo. php or shell.jsp ). The affected rules do not normalize whitespace before evaluating the file extension regex, so the dot-extension check fails to match. This issue has been patched in versions 3.3.9 and 4.25.0.

## References
- http://seclists.org/fulldisclosure/2026/Apr/0
- http://www.openwall.com/lists/oss-security/2026/03/29/2
- http://www.openwall.com/lists/oss-security/2026/04/18/4
- https://github.com/coreruleset/coreruleset/releases/tag/v3.3.9
- https://github.com/coreruleset/coreruleset/releases/tag/v4.25.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33691.json
- https://github.com/coreruleset/coreruleset/security/advisories/GHSA-rw5f-9w43-gv2w
- https://nvd.nist.gov/vuln/detail/CVE-2026-33691
- https://github.com/coreruleset/coreruleset/commit/2a8c63512811c5dd74472becebb79a783e68ff02
- https://github.com/coreruleset/coreruleset/pull/4546
- https://github.com/coreruleset/coreruleset/pull/4547
- https://github.com/coreruleset/coreruleset/pull/4548
