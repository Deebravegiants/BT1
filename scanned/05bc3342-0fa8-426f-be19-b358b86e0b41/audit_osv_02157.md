# [M] ALPINE-CVE-2021-28687

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-28687
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28687
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=4.12 <4.13.3-r0
- Alpine:v3.12: `xen` — affected >=4.12 <4.13.3-r0
- Alpine:v3.14: `xen` — affected >=4.12 <4.15.0-r0
- Alpine:v3.15: `xen` — affected >=4.12 <4.15.0-r0
- Alpine:v3.16: `xen` — affected >=4.12 <4.15.0-r0
- Alpine:v3.17: `xen` — affected >=4.12 <4.15.0-r0
- Alpine:v3.18: `xen` — affected >=4.12 <4.15.0-r0
- Alpine:v3.19: `xen` — affected >=4.12 <4.15.0-r0
- Alpine:v3.20: `xen` — affected >=4.12 <4.15.0-r0
- Alpine:v3.21: `xen` — affected >=4.12 <4.15.0-r0
- Alpine:v3.22: `xen` — affected >=4.12 <4.15.0-r0
- Alpine:v3.23: `xen` — affected >=4.12 <4.15.0-r0
- Alpine:v3.24: `xen` — affected >=4.12 <4.15.0-r0

## Details
HVM soft-reset crashes toolstack libxl requires all data structures passed across its public interface to be initialized before use and disposed of afterwards by calling a specific set of functions. Many internal data structures also require this initialize / dispose discipline, but not all of them. When the "soft reset" feature was implemented, the libxl__domain_suspend_state structure didn't require any initialization or disposal. At some point later, an initialization function was introduced for the structure; but the "soft reset" path wasn't refactored to call the initialization function. When a guest nwo initiates a "soft reboot", uninitialized data structure leads to an assert() when later code finds the structure in an unexpected state. The effect of this is to crash the process monitoring the guest. How this affects the system depends on the structure of the toolstack. For xl, this will have no security-relevant effect: every VM has its own independent monitoring process, which contains no state. The domain in question will hang in a crashed state, but can be destroyed by `xl destroy` just like any other non-cooperating domain. For daemon-based toolstacks linked against libxl, such as libvirt, this will crash the toolstack, losing the state of any in-progress operations (localized DoS), and preventing further administrator operations unless the daemon is configured to restart automatically (system-wide DoS). If crashes "leak" resources, then repeated crashes could use up resources, also causing a system-wide DoS.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28687
