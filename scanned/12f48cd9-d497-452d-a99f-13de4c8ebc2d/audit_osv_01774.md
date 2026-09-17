# [M] ALPINE-CVE-2020-14364

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14364
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.0 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:L/I:L/A:L)
Published: 2020-08-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14364
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.3-r3
- Alpine:v3.11: `xen` — affected >=0 <4.13.1-r3
- Alpine:v3.12: `xen` — affected >=0 <4.13.1-r3
- Alpine:v3.13: `xen` — affected >=0 <4.13.1-r5
- Alpine:v3.14: `xen` — affected >=0 <4.13.1-r5
- Alpine:v3.15: `xen` — affected >=0 <4.13.1-r5
- Alpine:v3.16: `xen` — affected >=0 <4.13.1-r5
- Alpine:v3.17: `xen` — affected >=0 <4.13.1-r5
- Alpine:v3.18: `xen` — affected >=0 <4.13.1-r5
- Alpine:v3.19: `xen` — affected >=0 <4.13.1-r5
- Alpine:v3.20: `xen` — affected >=0 <4.13.1-r5
- Alpine:v3.21: `xen` — affected >=0 <4.13.1-r5
- Alpine:v3.22: `xen` — affected >=0 <4.13.1-r5
- Alpine:v3.23: `xen` — affected >=0 <4.13.1-r5
- Alpine:v3.24: `xen` — affected >=0 <4.13.1-r5
- Alpine:v3.9: `xen` — affected >=0 <4.11.4-r1

## Details
An out-of-bounds read/write access flaw was found in the USB emulator of the QEMU in versions before 5.2.0. This issue occurs while processing USB packets from a guest when USBDevice 'setup_len' exceeds its 'data_buf[4096]' in the do_token_in, do_token_out routines. This flaw allows a guest user to crash the QEMU process, resulting in a denial of service, or the potential execution of arbitrary code with the privileges of the QEMU process on the host.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14364
