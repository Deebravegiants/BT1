# [H] CVE-2026-37229

## Summary
Severity: High
Advisory: CVE-2026-37229
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-37229
Type: osv

## Details
FlexRIC v2.0.0 contains a reachable assertion in e2ap_create_pdu() triggered when ASN.1 PER decoding fails. A remote unauthenticated attacker can send any non-PER byte sequence (e.g., a single 0x00 byte) over SCTP to the near-RT RIC (port 36421) or iApp (port 36422) to crash the process via SIGABRT. The assertion is reached before any protocol-level validation occurs. All three E2AP protocol versions (v1.01, v2.03, v3.01) are affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37229.json
- https://github.com/MinamiKotor1/oran-security-advisories-zhongnan-luo/blob/main/advisories/CVE-2026-37229.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-37229
- https://gitlab.eurecom.fr/mosaic5g/flexric
