# [C] ePA 3.x Integration: VAU Server Authentication Bypass via Circular Certificate Trust

## Summary
Severity: Critical
Advisory: CVE-2026-52723
Aliases: GHSA-q2jw-6c4w-86jc
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-52723
Type: osv

## Details
ePA 3.x Integration implements the authorization workflow and writes Medical Information Objects to Germany's electronic patient record. Prior to 1.3.0, ePA 3.x Integration performs VAU server certificate validation in app/vau/VAUProtokoll.py without anchoring the signed_vau_server_pub_keys and AUT_VAU_CertData certificate path to independent trusted material. A network-positioned attacker between the DiGA backend and the ePA system can intercept the VAU handshake, supply attacker-controlled certificate and key material, and satisfy the circular trust relationship. Because TLS certificate verification is also disabled in affected versions, no independent server-authentication layer prevents the attack. The attacker can impersonate the VAU server, control the negotiated session keys, and read or modify all encrypted VAU traffic. This issue is fixed in version 1.3.0.

## References
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/releases/tag/1.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52723.json
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/security/advisories/GHSA-q2jw-6c4w-86jc
- https://nvd.nist.gov/vuln/detail/CVE-2026-52723
- https://www.machinespirits.de/advisory/a1da93
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/commit/197c8c7fc41675f19c7f448696a2bc63fab9db5b
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/pull/12
