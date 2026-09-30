# [C] CVE-2020-36244

## Summary
Severity: Critical
Advisory: CVE-2020-36244
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-10
Source: https://osv.dev/vulnerability/CVE-2020-36244
Type: osv

## Details
The daemon in GENIVI diagnostic log and trace (DLT), is vulnerable to a heap-based buffer overflow that could allow an attacker to remotely execute arbitrary code on the DLT-Daemon (versions prior to 2.18.6).

## References
- https://github.com/GENIVI/dlt-daemon/issues/265
- https://us-cert.cisa.gov/ics/advisories/icsa-21-147-01
- https://github.com/GENIVI/dlt-daemon/compare/v2.18.5...v2.18.6
- https://lists.debian.org/debian-lts-announce/2022/12/msg00016.html
