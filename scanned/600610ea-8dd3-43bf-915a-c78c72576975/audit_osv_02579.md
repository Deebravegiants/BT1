# [C] ALPINE-CVE-2022-32221

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-32221
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-32221
Type: osv

## Affected
- Alpine:v3.15: `curl` — affected >=0 <7.80.0-r4
- Alpine:v3.16: `curl` — affected >=0 <7.83.1-r4
- Alpine:v3.17: `curl` — affected >=0 <7.86.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.86.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.86.0-r0
- Alpine:v3.20: `curl` — affected >=0 <7.86.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.86.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.86.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.86.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.86.0-r0

## Details
When doing HTTP(S) transfers, libcurl might erroneously use the read callback (`CURLOPT_READFUNCTION`) to ask for data to send, even when the `CURLOPT_POSTFIELDS` option has been set, if the same handle previously was used to issue a `PUT` request which used that callback. This flaw may surprise the application and cause it to misbehave and either send off the wrong data or use memory after free or similar in the subsequent `POST` request. The problem exists in the logic for a reused handle when it is changed from a PUT to a POST.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-32221
