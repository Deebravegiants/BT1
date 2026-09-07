# [C] AVideo has Authenticated Remote Code Execution via Unsafe Plugin ZIP Extraction

## Summary
Severity: Critical
Advisory: GHSA-v8jw-8w5p-23g3
CVE: CVE-2026-28502
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-v8jw-8w5p-23g3
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary
An authenticated Remote Code Execution (RCE) vulnerability was identified in AVideo related to the plugin upload/import functionality.

The issue allowed an authenticated administrator to upload a specially crafted ZIP archive containing executable server-side files. Due to insufficient validation of extracted file contents, the archive was extracted directly into a web-accessible plugin directory, allowing arbitrary PHP code execution.

## Vulnerability Type
- Remote Code Execution (RCE)
- CWE-434: Unrestricted Upload of File with Dangerous Type

## Affected Versions
- All versions up to and including 22.x.

## Fixed Version
- A fix is expected to be released in version 23.

## Root Cause
The system validated only the ZIP extension of uploaded plugin packages but did not enforce a strict allowlist of file types within the archive. Extracted files were placed directly in a web-accessible directory without preventing execution of server-side scripts.

## Impact
An authenticated administrator could execute arbitrary code on the server, resulting in full system compromise, including:
- Confidentiality loss
- Integrity loss
- Availability impact

## Remediation
Upgrade immediately to **AVideo version 23 or later**.

Version 23 introduces improved validation and secure handling of plugin extraction.

## Workarounds
If upgrade is not immediately possible:
- Disable plugin upload/import functionality.
- Configure the web server to prevent execution of PHP files inside plugin upload directories.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-v8jw-8w5p-23g3
- https://nvd.nist.gov/vuln/detail/CVE-2026-28502
- https://github.com/WWBN/AVideo/commit/b739aeeb9ce34aed9961d2c155d597810f8229db
- https://github.com/WWBN/AVideo
- https://github.com/WWBN/AVideo/releases/tag/24.0
