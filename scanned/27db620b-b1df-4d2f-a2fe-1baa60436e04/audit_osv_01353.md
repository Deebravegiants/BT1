# [C] ALPINE-CVE-2019-11708

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-11708
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11708
Type: osv

## Affected
- Alpine:v3.10: `mozjs60` — affected >=0 <60.7.2-r0
- Alpine:v3.11: `mozjs60` — affected >=0 <60.7.2-r0
- Alpine:v3.12: `mozjs60` — affected >=0 <60.7.2-r0

## Details
Insufficient vetting of parameters passed with the Prompt:Open IPC message between child and parent processes can result in the non-sandboxed parent process opening web content chosen by a compromised child process. When combined with additional vulnerabilities this could result in executing arbitrary code on the user's computer. This vulnerability affects Firefox ESR < 60.7.2, Firefox < 67.0.4, and Thunderbird < 60.7.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11708
