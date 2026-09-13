# [M] ALPINE-CVE-2026-42494

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-42494
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42494
Type: osv

## Affected
- Alpine:v3.21: `xen` — affected >=0 <4.19.6-r0
- Alpine:v3.22: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.23: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.24: `xen` — affected >=0 <4.21.2-r0

## Details
[This CNA information record relates to multiple CVEs; the
text explains which aspects/vulnerabilities correspond to which CVE.]

The directory and Rock Ridge / SUSP walk in libfsimage's iso9660 driver
derives several lengths directly from attacker-controlled on-disk fields
without validating them:

 * The directory loop itself assumes a good record length.  This is
   CVE-2026-42494.

 * The calculation of the System Use area may underflow.  This is
   CVE-2026-42495.

 * The Rock Ridge extension loop assumes a good (inner) record length.
   This is CVE-2026-62423.

 * The Rock Ridge NM record processing assumes a good entry length.
   This is CVE-2026-62424.

 * The Rock Ridge CE record processing assumes a good size and offset.
   This is CVE-2026-62425.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42494
