# [C] ALPINE-CVE-2025-48385

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-48385
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-48385
Type: osv

## Affected
- Alpine:v3.19: `git` — affected >=0 <2.43.7-r0
- Alpine:v3.20: `git` — affected >=0 <2.45.4-r0
- Alpine:v3.21: `git` — affected >=0 <2.47.3-r0
- Alpine:v3.22: `git` — affected >=0 <2.49.1-r0
- Alpine:v3.23: `git` — affected >=0 <2.50.1-r0
- Alpine:v3.24: `git` — affected >=0 <2.50.1-r0

## Details
Git is a fast, scalable, distributed revision control system with an unusually rich command set that provides both high-level operations and full access to internals. When cloning a repository Git knows to optionally fetch a bundle advertised by the remote server, which allows the server-side to offload parts of the clone to a CDN. The Git client does not perform sufficient validation of the advertised bundles, which allows the remote side to perform protocol injection. This protocol injection can cause the client to write the fetched bundle to a location controlled by the adversary. The fetched content is fully controlled by the server, which can in the worst case lead to arbitrary code execution. The use of bundle URIs is not enabled by default and can be controlled by the bundle.heuristic config option. Some cases of the vulnerability require that the adversary is in control of where a repository will be cloned to. This either requires social engineering or a recursive clone with submodules. These cases can thus be avoided by disabling recursive clones. This vulnerability is fixed in v2.43.7, v2.44.4, v2.45.4, v2.46.4, v2.47.3, v2.48.2, v2.49.1, and v2.50.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-48385
