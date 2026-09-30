# [M] ALPINE-CVE-2022-35260

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-35260
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-35260
Type: osv

## Affected
- Alpine:v3.17: `curl` — affected >=7.84.0 <7.86.0-r0
- Alpine:v3.18: `curl` — affected >=7.84.0 <7.86.0-r0
- Alpine:v3.19: `curl` — affected >=7.84.0 <7.86.0-r0
- Alpine:v3.20: `curl` — affected >=7.84.0 <7.86.0-r0
- Alpine:v3.21: `curl` — affected >=7.84.0 <7.86.0-r0
- Alpine:v3.22: `curl` — affected >=7.84.0 <7.86.0-r0
- Alpine:v3.23: `curl` — affected >=7.84.0 <7.86.0-r0
- Alpine:v3.24: `curl` — affected >=7.84.0 <7.86.0-r0

## Details
curl can be told to parse a `.netrc` file for credentials. If that file endsin a line with 4095 consecutive non-white space letters and no newline, curlwould first read past the end of the stack-based buffer, and if the readworks, write a zero byte beyond its boundary.This will in most cases cause a segfault or similar, but circumstances might also cause different outcomes.If a malicious user can provide a custom netrc file to an application or otherwise affect its contents, this flaw could be used as denial-of-service.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-35260
