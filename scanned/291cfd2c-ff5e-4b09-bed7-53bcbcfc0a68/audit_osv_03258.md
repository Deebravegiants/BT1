# [M] ALPINE-CVE-2025-31115

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-31115
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-31115
Type: osv

## Affected
- Alpine:v3.18: `xz` — affected >=0 <5.4.3-r1
- Alpine:v3.19: `xz` — affected >=0 <5.4.5-r1
- Alpine:v3.20: `xz` — affected >=0 <5.6.2-r1
- Alpine:v3.21: `xz` — affected >=0 <5.6.3-r1
- Alpine:v3.22: `xz` — affected >=0 <5.8.1-r0
- Alpine:v3.23: `xz` — affected >=0 <5.8.1-r0
- Alpine:v3.24: `xz` — affected >=0 <5.8.1-r0

## Details
XZ Utils provide a general-purpose data-compression library plus command-line tools. In XZ Utils 5.3.3alpha to 5.8.0, the multithreaded .xz decoder in liblzma has a bug where invalid input can at least result in a crash. The effects include heap use after free and writing to an address based on the null pointer plus an offset. Applications and libraries that use the lzma_stream_decoder_mt function are affected. The bug has been fixed in XZ Utils 5.8.1, and the fix has been committed to the v5.4, v5.6, v5.8, and master branches in the xz Git repository. No new release packages will be made from the old stable branches, but a standalone patch is available that applies to all affected releases.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-31115
