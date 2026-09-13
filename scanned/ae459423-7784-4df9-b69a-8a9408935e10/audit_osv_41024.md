# [H] CANBoat - Off-by-One Global Buffer Overflow in searchForPgn()

## Summary
Severity: High
Advisory: CVE-2026-56790
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-56790
Type: osv

## Details
CANBoat through 6.22, fixed in commit a5a22b7, contains an off-by-one global buffer overflow in the searchForPgn() function in analyzer/pgn.c that allows remote attackers to crash the application. Attackers can deliver a crafted NMEA-2000 message with an out-of-range PGN value over CAN bus or N2K-over-IP to trigger an out-of-bounds array access and denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56790.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56790
- https://www.vulncheck.com/advisories/canboat-off-by-one-global-buffer-overflow-in-searchforpgn
- https://github.com/canboat/canboat/pull/649
- https://github.com/canboat/canboat/commit/a5a22b74b9ac5688019cba62669df08562cebd6f
- https://github.com/canboat/canboat
- https://github.com/canboat/canboat/issues/644
