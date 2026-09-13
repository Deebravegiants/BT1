# [M] ALPINE-CVE-2025-43857

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-43857
Ecosystem: Alpine:v3.20, Alpine:v3.21
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-04-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-43857
Type: osv

## Affected
- Alpine:v3.20: `ruby-net-imap` — affected >=0 <0.4.22-r0
- Alpine:v3.21: `ruby-net-imap` — affected >=0 <0.4.22-r0

## Details
Net::IMAP implements Internet Message Access Protocol (IMAP) client functionality in Ruby. Prior to versions 0.5.7, 0.4.20, 0.3.9, and 0.2.5, there is a possibility for denial of service by memory exhaustion when net-imap reads server responses. At any time while the client is connected, a malicious server can send can send a "literal" byte count, which is automatically read by the client's receiver thread. The response reader immediately allocates memory for the number of bytes indicated by the server response. This should not be an issue when securely connecting to trusted IMAP servers that are well-behaved. It can affect insecure connections and buggy, untrusted, or compromised servers (for example, connecting to a user supplied hostname). This issue has been patched in versions 0.5.7, 0.4.20, 0.3.9, and 0.2.5.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-43857
