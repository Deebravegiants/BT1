# [M] JLSEC-2026-1240

## Summary
Severity: Medium
Advisory: JLSEC-2026-1240
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N/E:P/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/JLSEC-2026-1240
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=0 <2.11.5+0

## Details
Use After Free in libxml2's xmlParseInternalSubset from GNOME libxml2 version 2.9.11 to 2.11.0 allows a remote attacker to cause a denial-of-service via maliciously crafted XML input with improper entity resolution handling.

## References
- https://bugs.launchpad.net/ubuntu/+source/libxml2/+bug/2141260
- https://gitlab.gnome.org/GNOME/libxml2/-/work_items/1058
