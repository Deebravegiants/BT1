# [H] ePA 3.x Integration: TLS Certificate Verification Universally Disabled

## Summary
Severity: High
Advisory: CVE-2026-50578
Aliases: GHSA-j9m9-pmwv-hwwr
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-50578
Type: osv

## Details
ePA 3.x Integration implements the authorization workflow and writes Medical Information Objects to Germany's electronic patient record. Prior to 1.3.0, ePA 3.x Integration disables TLS certificate verification for both ePA connections in app/vau/VAUProtokoll.py and Konnektor connections in app/konnektor/Konnektor.py. A network-positioned attacker can present an arbitrary certificate, terminate the TLS connection, and intercept ePA traffic. The VAU protocol does not provide an effective fallback because its application-layer certificate validation is also broken in affected versions. The Konnektor session uses self.session.verify set to False while the client authenticates with self.session.cert, so an attacker impersonating the Konnektor can receive the client's mutual TLS certificate exchange and observe smartcard operations. This issue is fixed in version 1.3.0.

## References
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/releases/tag/1.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50578.json
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/security/advisories/GHSA-j9m9-pmwv-hwwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-50578
- https://www.machinespirits.de/advisory/4b68b0
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/commit/0d94a76aa4d57a849f0c18fb3d6d337ec2505170
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/pull/9
