# [C] Git source checkout from a bundle file could lead to command injection

## Summary
Severity: Critical
Advisory: CVE-2026-15793
Aliases: GHSA-hw3h-2gp9-cxpv
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-15793
Type: osv

## Details
BuildKit custom frontends or clients using the raw low-level API can set git.checkoutbundle=true when checking out Git sources. If the Git source is malicious, this could lead to a crafted command invocation on the host.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15793.json
- https://github.com/moby/buildkit/security/advisories/GHSA-hw3h-2gp9-cxpv
- https://nvd.nist.gov/vuln/detail/CVE-2026-15793
