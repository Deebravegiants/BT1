# [H] ALPINE-CVE-2024-33655

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-33655
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-33655
Type: osv

## Affected
- Alpine:v3.17: `unbound` — affected >=0 <1.20.0-r0
- Alpine:v3.18: `unbound` — affected >=0 <1.20.0-r0
- Alpine:v3.19: `unbound` — affected >=0 <1.20.0-r0
- Alpine:v3.20: `unbound` — affected >=0 <1.20.0-r0
- Alpine:v3.21: `unbound` — affected >=0 <1.20.0-r0
- Alpine:v3.22: `unbound` — affected >=0 <1.20.0-r0
- Alpine:v3.23: `unbound` — affected >=0 <1.20.0-r0
- Alpine:v3.24: `unbound` — affected >=0 <1.20.0-r0

## Details
The DNS protocol in RFC 1035 and updates allows remote attackers to cause a denial of service (resource consumption) by arranging for DNS queries to be accumulated for seconds, such that responses are later sent in a pulsing burst (which can be considered traffic amplification in some cases), aka the "DNSBomb" issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-33655
