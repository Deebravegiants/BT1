# [H] ICEcoder through 8.1 Path Traversal via oldFileName Parameter

## Summary
Severity: High
Advisory: CVE-2026-64838
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-64838
Type: osv

## Details
ICEcoder versions through 8.1 fail to properly validate the oldFileName parameter in file move and rename operations, allowing authenticated users to relocate files from outside the document root. Attackers can use path traversal sequences in oldFileName to move files writable by the PHP process into the web-accessible project directory, disclosing file contents and deleting originals.

## References
- https://packagist.org/packages/icecoder/icecoder
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64838.json
- https://github.com/Caycon/cve-advisories/blob/main/2026/ICEcoder/CVE-2026-64838.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-64838
- https://www.vulncheck.com/advisories/icecoder-through-8.1-path-traversal-via-oldfilename-parameter
- https://github.com/icecoder/ICEcoder
- https://github.com/icecoder/ICEcoder/blob/4a61847ef7bb0360735cf1d55c45e5de9746e24e/lib/file-control.php#L198
