# [M] Authenticated Path Traversal in AIL Framework Investigation Downloads Allows Arbitrary File Read

## Summary
Severity: Medium
Advisory: CVE-2026-56448
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N/S:P)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-56448
Type: osv

## Details
A path traversal vulnerability exists in AIL Framework before the release containing commit 0041456af25da0cdea1c1c4624e46baff2731d8f. An authenticated AIL user can supply crafted object identifiers through the investigation workflow to cause file paths to resolve outside the intended image, favicon, or screenshot storage directories. This may allow the attacker to download and read arbitrary files that are accessible to the AIL process.

The issue occurs because user-controlled path components were joined with application storage paths without verifying that the resolved path remained within the expected directory. The affected download functionality could then include the contents of such files in a generated archive.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56448.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56448
- https://github.com/ail-project/ail-framework/commit/0041456af25da0cdea1c1c4624e46baff2731d8f
- https://github.com/ail-project/ail-framework
