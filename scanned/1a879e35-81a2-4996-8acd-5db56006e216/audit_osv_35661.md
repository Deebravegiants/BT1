# [H] CVE-2026-12246

## Summary
Severity: High
Advisory: CVE-2026-12246
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-12246
Type: osv

## Details
NSD version 4.14.0 introduced a bug where a specially crafted APL RR, with an adflength larger than permitted for the address family will overwrite the stack when the zone is written to disk, with a maximum of 111 attacker controlled bytes.

## References
- https://www.nlnetlabs.nl/downloads/nsd/CVE-2026-12246.txt
