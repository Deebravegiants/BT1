# [M] ALPINE-CVE-2023-42669

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-42669
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-42669
Type: osv

## Affected
- Alpine:v3.18: `samba` — affected >=4.0.0 <4.18.8-r0
- Alpine:v3.19: `samba` — affected >=4.0.0 <4.18.8-r0
- Alpine:v3.20: `samba` — affected >=4.0.0 <4.18.8-r0
- Alpine:v3.21: `samba` — affected >=4.0.0 <4.18.8-r0
- Alpine:v3.22: `samba` — affected >=4.0.0 <4.18.8-r0
- Alpine:v3.23: `samba` — affected >=4.0.0 <4.18.8-r0
- Alpine:v3.24: `samba` — affected >=4.0.0 <4.18.8-r0

## Details
A vulnerability was found in Samba's "rpcecho" development server, a non-Windows RPC server used to test Samba's DCE/RPC stack elements. This vulnerability stems from an RPC function that can be blocked indefinitely. The issue arises because the "rpcecho" service operates with only one worker in the main RPC task, allowing calls to the "rpcecho" server to be blocked for a specified time, causing service disruptions. This disruption is triggered by a "sleep()" call in the "dcesrv_echo_TestSleep()" function under specific conditions. Authenticated users or attackers can exploit this vulnerability to make calls to the "rpcecho" server, requesting it to block for a specified duration, effectively disrupting most services and leading to a complete denial of service on the AD DC. The DoS affects all other services as "rpcecho" runs in the main RPC task.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-42669
