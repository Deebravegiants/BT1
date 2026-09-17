# [M] CVE-2019-18923

## Summary
Severity: Medium
Advisory: CVE-2019-18923
Aliases: GHSA-jg2r-qf99-4wvr
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-11-13
Source: https://osv.dev/vulnerability/CVE-2019-18923
Type: osv

## Details
Insufficient content type validation of proxied resources in go-camo before 2.1.1 allows a remote attacker to serve arbitrary content from go-camo's origin.

## References
- https://github.com/cactus/go-camo/blob/505862f7bf14c8b6ff945734d5f3fdcd929e45dd/pkg/camo/proxy.go#L453-L460
- https://github.com/cactus/go-camo/security/advisories/GHSA-jg2r-qf99-4wvr
