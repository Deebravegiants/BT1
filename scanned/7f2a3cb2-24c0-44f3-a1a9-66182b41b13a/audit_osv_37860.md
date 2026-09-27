# [M] CVE-2026-33603

## Summary
Severity: Medium
Advisory: CVE-2026-33603
CVSS: 6.8 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-33603
Type: osv

## Details
Attacker can use a specially crafted base64 exchange between Dovecot and Client to fake SCRAM TLS channel binding. This requires that the attacker is able to position itself between Dovecot and the client connection. If successful, the attacker can eavesdrop communications between Dovecot and client as MITM proxy. Install fixed version. No publicly available exploits are known.

## References
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0002.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33603.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33603
