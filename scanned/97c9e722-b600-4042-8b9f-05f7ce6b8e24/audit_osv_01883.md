# [M] ALPINE-CVE-2020-25600

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-25600
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25600
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=4.4.0 <4.12.3-r4
- Alpine:v3.11: `xen` — affected >=4.4.0 <4.13.1-r4
- Alpine:v3.12: `xen` — affected >=4.4.0 <4.13.1-r4
- Alpine:v3.13: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.14: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.15: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.16: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.17: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.18: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.19: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.20: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.21: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.22: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.23: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.24: `xen` — affected >=4.4.0 <4.14.0-r1
- Alpine:v3.9: `xen` — affected >=4.4.0 <4.11.4-r2

## Details
An issue was discovered in Xen through 4.14.x. Out of bounds event channels are available to 32-bit x86 domains. The so called 2-level event channel model imposes different limits on the number of usable event channels for 32-bit x86 domains vs 64-bit or Arm (either bitness) ones. 32-bit x86 domains can use only 1023 channels, due to limited space in their shared (between guest and Xen) information structure, whereas all other domains can use up to 4095 in this model. The recording of the respective limit during domain initialization, however, has occurred at a time where domains are still deemed to be 64-bit ones, prior to actually honoring respective domain properties. At the point domains get recognized as 32-bit ones, the limit didn't get updated accordingly. Due to this misbehavior in Xen, 32-bit domains (including Domain 0) servicing other domains may observe event channel allocations to succeed when they should really fail. Subsequent use of such event channels would then possibly lead to corruption of other parts of the shared info structure. An unprivileged guest may cause another domain, in particular Domain 0, to misbehave. This may lead to a Denial of Service (DoS) for the entire system. All Xen versions from 4.4 onwards are vulnerable. Xen versions 4.3 and earlier are not vulnerable. Only x86 32-bit domains servicing other domains are vulnerable. Arm systems, as well as x86 64-bit domains, are not vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25600
