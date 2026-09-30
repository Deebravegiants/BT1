# [H] Server-Side Request Forgery (SSRF) in stangirard/quivr

## Summary
Severity: High
Advisory: CVE-2024-5885
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2024-06-27
Source: https://osv.dev/vulnerability/CVE-2024-5885
Type: osv

## Details
stangirard/quivr version 0.0.236 contains a Server-Side Request Forgery (SSRF) vulnerability. The application does not provide sufficient controls when crawling a website, allowing an attacker to access applications on the local network. This vulnerability could allow a malicious user to gain access to internal servers, the AWS metadata endpoint, and capture Supabase data.

## References
- https://huntr.com/bounties/c178bf48-1d4a-4743-87ca-4cc8e475d274
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5885.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5885
