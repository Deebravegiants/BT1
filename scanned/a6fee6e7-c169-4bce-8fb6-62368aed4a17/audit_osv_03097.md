# [H] ALPINE-CVE-2024-43394

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-43394
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-43394
Type: osv

## Affected
- Alpine:v3.19: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.64-r0

## Details
Server-Side Request Forgery (SSRF) in Apache HTTP Server on Windows allows to potentially leak NTLM hashes to a malicious server via 
mod_rewrite or apache expressions that pass unvalidated request input.

This issue affects Apache HTTP Server: from 2.4.0 through 2.4.63.

Note:  The Apache HTTP Server Project will be setting a higher bar for accepting vulnerability reports regarding SSRF via UNC paths. 

The server offers limited protection against administrators directing the server to open UNC paths.
Windows servers should limit the hosts they will connect over via SMB based on the nature of NTLM authentication.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-43394
