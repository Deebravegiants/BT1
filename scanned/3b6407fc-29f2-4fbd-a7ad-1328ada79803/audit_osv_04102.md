# [H] Apache HTTP Server: SSRF on Windows due to UNC paths

## Summary
Severity: High
Advisory: BIT-apache-2024-43394
Aliases: CVE-2024-43394
Ecosystem: Bitnami
Published: 2025-07-16
Source: https://osv.dev/vulnerability/BIT-apache-2024-43394
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.0 <2.4.64

## Details
Server-Side Request Forgery (SSRF) in Apache HTTP Server on Windows allows to potentially leak NTLM hashes to a malicious server via 
mod_rewrite or apache expressions that pass unvalidated request input.

This issue affects Apache HTTP Server: from 2.4.0 through 2.4.63.

Note:  The Apache HTTP Server Project will be setting a higher bar for accepting vulnerability reports regarding SSRF via UNC paths. 

The server offers limited protection against administrators directing the server to open UNC paths.
Windows servers should limit the hosts they will connect over via SMB based on the nature of NTLM authentication.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-43394
- http://www.openwall.com/lists/oss-security/2025/07/10/2
- http://www.openwall.com/lists/oss-security/2025/07/10/5
- https://lists.debian.org/debian-lts-announce/2025/08/msg00009.html
