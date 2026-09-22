# [C] Hydra - Stack Buffer Overflow in NTLM Authentication Handler

## Summary
Severity: Critical
Advisory: CVE-2026-56766
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-56766
Type: osv

## Details
Hydra through 9.7, fixed in commit 9cc84c2, contains a stack buffer overflow in NTLM authentication across SMTP, POP3, IMAP, NNTP, HTTP, HTTP-Proxy, and HTTP-Proxy-Urlenum modules when processing malicious NTLM Type-2 challenges. A malicious server can send a crafted NTLM Type-2 challenge with an excessively long domain string, causing base64-encoded response data to overflow a 500-byte stack buffer by 18 to 330 bytes, enabling remote code execution on systems without stack protection.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56766.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56766
- https://www.vulncheck.com/advisories/hydra-stack-buffer-overflow-in-ntlm-authentication-handler
- https://github.com/vanhauser-thc/thc-hydra/commit/9cc84c20e75f5fef6bb1790bb9ada2afad2204e2
- https://github.com/vanhauser-thc/thc-hydra
