# [H] CVE-2026-37228

## Summary
Severity: High
Advisory: CVE-2026-37228
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-37228
Type: osv

## Details
FlexRIC v2.0.0 contains a reachable assertion in e2ap_recv_sctp_msg() (src/lib/ep/e2ap_ep.c). The function allocates a fixed 32KB receive buffer and enforces assert(rc < len) on the sctp_recvmsg() return value. A remote unauthenticated attacker can send a single SCTP message with payload >= 32,768 bytes to crash the near-RT RIC, iApp, E2 Agent, or xApp process via SIGABRT. No valid E2AP PDU is required. All four SCTP endpoint types (ports 36421 and 36422) share this vulnerable code path. In Release builds (NDEBUG), the stripped assertion leads to a signed-to-unsigned integer overflow and potential out-of-bounds read.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37228.json
- https://github.com/MinamiKotor1/oran-security-advisories-zhongnan-luo/blob/main/advisories/CVE-2026-37228.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-37228
- https://gitlab.eurecom.fr/mosaic5g/flexric
