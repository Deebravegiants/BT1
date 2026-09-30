# [C] ICEcoder through 8.1 Path Traversal via Ineffective File::check() Confinement

## Summary
Severity: Critical
Advisory: CVE-2026-64836
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-64836
Type: osv

## Details
ICEcoder versions through 8.1 contain a path traversal vulnerability in the file-control endpoint due to a logic error in the document-root confinement check. The File::check() validation function compares realpath() to boolean true, which never succeeds, allowing authenticated attackers to submit traversal sequences or absolute paths in the file parameter to read, write, or delete files outside the configured document root.

## References
- https://packagist.org/packages/icecoder/icecoder
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64836.json
- https://github.com/Caycon/cve-advisories/blob/main/2026/ICEcoder/CVE-2026-64836.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-64836
- https://www.vulncheck.com/advisories/icecoder-through-8.1-path-traversal-via-ineffective-file-check-confinement
- https://github.com/icecoder/ICEcoder
- https://github.com/icecoder/ICEcoder/blob/4a61847ef7bb0360735cf1d55c45e5de9746e24e/classes/File.php#L70
