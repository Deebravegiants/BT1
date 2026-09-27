# [M] NanaZip .NET Single-File Manifest Parser Vulnerable to Out-of-Bounds Read via Unchecked RelativePathLength

## Summary
Severity: Medium
Advisory: CVE-2026-27709
Aliases: GHSA-vr4w-xc78-w6fv
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27709
Type: osv

## Details
NanaZip is an open source file archive. Starting in version 5.0.1252.0 and prior to versions 6.0.1638.0 and 6.5.1638.0, NanaZip’s `.NET Single File Application` parser has an out-of-bounds read vulnerability in manifest parsing. A crafted bundle can provide a malformed `RelativePathLength` so the parser constructs a `std::string` from memory beyond `HeaderBuffer`, leading to crash and potential in-process memory disclosure. Versions 6.0.1638.0 and 6.5.1638.0 fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27709.json
- https://github.com/M2Team/NanaZip/security/advisories/GHSA-vr4w-xc78-w6fv
- https://nvd.nist.gov/vuln/detail/CVE-2026-27709
