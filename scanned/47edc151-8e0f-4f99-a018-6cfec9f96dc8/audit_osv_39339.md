# [H] HTMLy CMS 3.1.1 Path Traversal via oldfile Parameter in Autosave

## Summary
Severity: High
Advisory: CVE-2026-45233
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-45233
Type: osv

## Details
HTMLy CMS through 3.1.1 contains a path traversal vulnerability that allows low-privileged authenticated attackers to relocate arbitrary files by supplying directory traversal sequences in the oldfile parameter at the admin autosave endpoint. Attackers can pass unsanitized traversal sequences directly to file_exists() and rename() functions in admin.php without canonicalization or directory boundary enforcement to cause unintended relocation of any file writable by the web server process to an attacker-specified draft location.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45233.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45233
- https://www.vulncheck.com/advisories/htmly-cms-path-traversal-via-oldfile-parameter-in-autosave
- https://github.com/danpros/htmly
- https://gist.github.com/mrgr4yhat/c4df971eafa272ac8c86c15e2829b7fe
