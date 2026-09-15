# [M] Keploy 3.1.0-3.6.25 Unauthenticated TLS Key Exposure

## Summary
Severity: Medium
Advisory: CVE-2026-82641
Aliases: GHSA-p79c-x224-cv8h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-82641
Type: osv

## Details
Keploy versions 3.1.0 through 3.6.25, fixed in 3.6.26, bind the agent control-plane HTTP server to all interfaces without authentication, exposing endpoints that stream TLS session keys and traffic data. Attackers can access the /agent/pcap/keylog endpoint to retrieve NSS keylog lines and decrypt recorded TLS traffic, or invoke /agent/stop and /agent/storemocks to manipulate recording sessions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82641.json
- https://github.com/keploy/keploy/releases/tag/v3.6.26
- https://github.com/keploy/keploy/security/advisories/GHSA-p79c-x224-cv8h
- https://nvd.nist.gov/vuln/detail/CVE-2026-82641
- https://www.vulncheck.com/advisories/keploy-3.1.0-through-3.6.25-unauthenticated-tls-key-exposure
- https://github.com/keploy/keploy/pull/4451
- https://github.com/keploy/keploy/commit/a6257d2b3184b85eb30edad345464aa292297b83
- https://github.com/keploy/keploy
- https://github.com/keploy/keploy/issues/4394
