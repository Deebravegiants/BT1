# [H] ePA 3.x Integration: AES-GCM Nonce Reuse via Frozen VAU Request Counter

## Summary
Severity: High
Advisory: CVE-2026-50577
Aliases: GHSA-vmfm-3f7g-r9qg
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-50577
Type: osv

## Details
ePA 3.x Integration implements the authorization workflow and writes Medical Information Objects to Germany's electronic patient record. Prior to 1.3.0, ePA 3.x Integration leaves request_counter unchanged in app/vau/VAUProtokoll.py while constructing VAU messages. The frozen client request counter causes the server side to reuse AES-GCM nonce and key combinations across responses. A network attacker who collects repeated ciphertexts can recover the XOR of plaintexts and use predictable inner HTTP headers and JSON fields to recover sensitive data, including patient health records. Repeated nonces can also enable recovery of the GHASH authentication key through the Joux forbidden attack, allowing forged AES-GCM messages and injection of malicious responses. The response-counter check also fails to maintain last_response_counter, weakening replay and ordering validation. This issue is fixed in version 1.3.0.

## References
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/releases/tag/1.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50577.json
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/security/advisories/GHSA-vmfm-3f7g-r9qg
- https://nvd.nist.gov/vuln/detail/CVE-2026-50577
- https://www.machinespirits.de/advisory/df27cd
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/commit/85c4c516088c38b9cf2343f388ad67a6744e9814
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/pull/10
