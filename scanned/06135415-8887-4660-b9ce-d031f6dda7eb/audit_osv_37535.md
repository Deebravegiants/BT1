# [M] Istio JWKS resolver to prevent private key material from being exposed when JWKS fetch fails.

## Summary
Severity: Medium
Advisory: CVE-2026-31837
Aliases: GHSA-v75c-crr9-733c
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-31837
Type: osv

## Details
Istio is an open platform to connect, manage, and secure microservices. Prior to 1.29.1, 1.28.5, and 1.27.8, a user of Istio is impacted if the JWKS resolver becomes unavailable or the fetch fails, exposing hardcoded defaults regardless of use of the RequestAuthentication resource. This vulnerability is fixed in 1.29.1, 1.28.5, and 1.27.8.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-31837.json
- https://access.redhat.com/errata/RHSA-2026:10184
- https://access.redhat.com/errata/RHSA-2026:5948
- https://access.redhat.com/errata/RHSA-2026:5950
- https://access.redhat.com/errata/RHSA-2026:5952
- https://access.redhat.com/security/cve/CVE-2026-31837
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31837.json
- https://github.com/istio/istio/security/advisories/GHSA-v75c-crr9-733c
- https://nvd.nist.gov/vuln/detail/CVE-2026-31837
- https://bugzilla.redhat.com/show_bug.cgi?id=2446344
