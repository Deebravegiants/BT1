# [M] gitoxide before 0.37.1 HTTP Basic credential leak via URL parsing

## Summary
Severity: Medium
Advisory: CVE-2026-82247
Aliases: GHSA-jrcm-326h-gpp8
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82247
Type: osv

## Details
gitoxide's gix-url crate (<= 0.32.0, fixed in 0.37.1) uses a hand-rolled URL parser that does not treat '?' or '#' as terminating the authority component, contrary to RFC 3986. As a consequence, gix-transport's HTTP redirect identity guard (can_reuse_identity) compares the wrong host and fails open. An attacker controlling a redirect response can craft a Location header of the form <attacker-authority>?@<original-authority> so that gitoxide sends the caller's HTTP Basic Authorization credentials to an unintended host. gix-transport is affected in versions <= 0.49.0 (fixed in 0.58.1).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82247.json
- https://github.com/GitoxideLabs/gitoxide/security/advisories/GHSA-jrcm-326h-gpp8
- https://nvd.nist.gov/vuln/detail/CVE-2026-82247
- https://www.vulncheck.com/advisories/gitoxide-before-0.37.1-http-basic-credential-leak-via-url-parsing
