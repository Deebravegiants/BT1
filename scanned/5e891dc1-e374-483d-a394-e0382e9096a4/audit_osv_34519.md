# [H] Ts3 Manager: Unauthenticated Denial of Service possible through specially crafted Unicode input

## Summary
Severity: High
Advisory: CVE-2025-61582
Aliases: GHSA-4cq4-hp4f-8w7p
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-61582
Type: osv

## Details
TS3 Manager is modern web interface for maintaining Teamspeak3 servers. A Denial of Dervice vulnerability has been identified in versions 2.2.1 and earlier. The vulnerability permits an unauthenticated actor to crash the application through the submission of specially crafted Unicode input, requiring no prior authentication or privileges. The flaw manifests when Unicode tag characters are submitted to the Server field on the login page. The application fails to properly handle these characters during the ASCII conversion process, resulting in an unhandled exception that terminates the application within four to five seconds of submission. This issue is fixed in version 2.2.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61582.json
- https://github.com/joni1802/ts3-manager/security/advisories/GHSA-4cq4-hp4f-8w7p
- https://nvd.nist.gov/vuln/detail/CVE-2025-61582
- https://github.com/joni1802/ts3-manager/commit/3a069915f97a6f5dae1fe0b2e32aa11a69d83b5e
