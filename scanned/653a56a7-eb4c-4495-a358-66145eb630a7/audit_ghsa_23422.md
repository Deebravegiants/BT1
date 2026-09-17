# [M] nv-websocket-client allows attackers to spoof SSL/TLS servers via an arbitrary valid certificate

## Summary
Severity: Medium
Advisory: GHSA-4hxv-95rc-jqg7
CVE: CVE-2017-1000209
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4hxv-95rc-jqg7
Type: github-advisory

## Affected
- Maven: `com.neovisionaries:nv-websocket-client` — affected >=0 <2.1

## Details
The Java WebSocket client nv-websocket-client does not verify that the server hostname matches a domain name in the subject's Common Name (CN) or subjectAltName field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL/TLS servers via an arbitrary valid certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000209
- https://github.com/TakahikoKawasaki/nv-websocket-client/pull/107
