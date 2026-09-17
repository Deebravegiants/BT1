# [H] CVE-2025-65271

## Summary
Severity: High
Advisory: CVE-2025-65271
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-65271
Type: osv

## Details
Client-side template injection (CSTI) in Azuriom CMS admin dashboard allows a low-privilege user to execute arbitrary template code in the context of an administrator's session. This can occur via plugins or dashboard components that render untrusted user input, potentially enabling privilege escalation to an administrative account. Fixed in Azuriom 1.2.7.

## References
- https://www.github.com/Azuriom/Azuriom
- https://www.github.com/Azuriom/Azuriom/commit/0289175547319add814dcb526e8ba034f1ebc3ec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65271.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65271
- https://github.com/Azuriom/Azuriom/commit/0289175547319add814dcb526e8ba034f1ebc3ec
- https://github.com/1337Skid/CVE-2025-65271
- https://github.com/Azuriom/Azuriom
