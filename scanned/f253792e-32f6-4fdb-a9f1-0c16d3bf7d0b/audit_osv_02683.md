# [H] ALPINE-CVE-2022-42332

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-42332
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42332
Type: osv

## Affected
- Alpine:v3.15: `xen` — affected >=3.2.0 <4.15.5-r0
- Alpine:v3.16: `xen` — affected >=3.2.0 <4.16.4-r0
- Alpine:v3.17: `xen` — affected >=3.2.0 <4.16.4-r0
- Alpine:v3.18: `xen` — affected >=3.2.0 <4.17.0-r5
- Alpine:v3.19: `xen` — affected >=3.2.0 <4.17.0-r5
- Alpine:v3.20: `xen` — affected >=3.2.0 <4.17.0-r5
- Alpine:v3.21: `xen` — affected >=3.2.0 <4.17.0-r5
- Alpine:v3.22: `xen` — affected >=3.2.0 <4.17.0-r5
- Alpine:v3.23: `xen` — affected >=3.2.0 <4.17.0-r5
- Alpine:v3.24: `xen` — affected >=3.2.0 <4.17.0-r5

## Details
x86 shadow plus log-dirty mode use-after-free In environments where host assisted address translation is necessary but Hardware Assisted Paging (HAP) is unavailable, Xen will run guests in so called shadow mode. Shadow mode maintains a pool of memory used for both shadow page tables as well as auxiliary data structures. To migrate or snapshot guests, Xen additionally runs them in so called log-dirty mode. The data structures needed by the log-dirty tracking are part of aformentioned auxiliary data. In order to keep error handling efforts within reasonable bounds, for operations which may require memory allocations shadow mode logic ensures up front that enough memory is available for the worst case requirements. Unfortunately, while page table memory is properly accounted for on the code path requiring the potential establishing of new shadows, demands by the log-dirty infrastructure were not taken into consideration. As a result, just established shadow page tables could be freed again immediately, while other code is still accessing them on the assumption that they would remain allocated.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42332
