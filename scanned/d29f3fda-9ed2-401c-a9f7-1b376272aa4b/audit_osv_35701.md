# [C] Arbitrary file write in Language Servers for AWS

## Summary
Severity: Critical
Advisory: CVE-2026-12958
Aliases: GHSA-6v3r-4p5c-mrp5
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-12958
Type: osv

## Details
Missing symlink validation in Language Servers for AWS may allow an arbitrary file write outside of the workspace trust boundary. This may occur when a local user opens a workspace with a maliciously crafted symlink that resolves to a file path outside the workspace trust boundary.



To remediate this issue, users should upgrade to version 1.69.0 or higher.

## References
- https://aws.amazon.com/security/security-bulletins/2026-047-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12958.json
- https://github.com/aws/language-servers/security/advisories/GHSA-6v3r-4p5c-mrp5
- https://nvd.nist.gov/vuln/detail/CVE-2026-12958
