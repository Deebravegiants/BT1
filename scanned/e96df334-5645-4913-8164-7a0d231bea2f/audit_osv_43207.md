# [H] filebrowser before v2.63.21 Access Rule Bypass via Path Canonicalization

## Summary
Severity: High
Advisory: CVE-2026-72835
Aliases: GHSA-fgm5-pw99-w2p7
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-72835
Type: osv

## Details
filebrowser versions before v2.63.21 fail to canonicalize paths before evaluating access rules, allowing authenticated users to bypass administrator-defined deny rules using case-variant or backslash-separated paths. Attackers can request files with alternate path representations that match no rule but resolve to the same filesystem object, gaining unauthorized access to denied files within their scope.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72835.json
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-fgm5-pw99-w2p7
- https://nvd.nist.gov/vuln/detail/CVE-2026-72835
- https://www.vulncheck.com/advisories/filebrowser-before-access-rule-bypass-via-path-canonicalization
