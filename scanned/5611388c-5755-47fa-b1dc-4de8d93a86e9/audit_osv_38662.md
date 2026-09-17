# [M] jq: Embedded NUL truncates top-level jq programs loaded with -f

## Summary
Severity: Medium
Advisory: CVE-2026-41256
Aliases: GHSA-vf2h-chrj-q3fg
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-41256
Type: osv

## Details
jq is a command-line JSON processor. In 1.8.1 and earlier, Top-level jq programs loaded from a file with -f are truncated at the first embedded NUL byte on current upstream HEAD. A crafted filter file such as . followed by \x00 and arbitrary suffix compiles and executes as only the prefix before the NUL. This leaves jq with a post-CVE-2026-33948 prefix/full-buffer mismatch on the compilation path even though the JSON parser path has already been fixed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41256.json
- https://github.com/jqlang/jq/security/advisories/GHSA-vf2h-chrj-q3fg
- https://nvd.nist.gov/vuln/detail/CVE-2026-41256
