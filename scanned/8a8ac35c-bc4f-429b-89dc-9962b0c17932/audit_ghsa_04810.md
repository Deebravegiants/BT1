# [C] Paymenter vulnerable to Remote Code Execution via public file uploads

## Summary
Severity: Critical
Advisory: GHSA-5pm9-r2m8-rcmj
CVE: CVE-2025-58048
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-5pm9-r2m8-rcmj
Type: github-advisory

## Affected
- Packagist: `paymenter/paymenter` — affected >=0 <1.2.11

## Details
### Impact

The ticket attachments functionality in Paymenter allows a malicious authenticated user to upload arbitrary files.

With the ability to execute arbitrary code, this vulnerability can be exploited in numerous ways, including but not limited to:
- Extracting sensitive data from the database (e.g. customer information).
- Reading credentials from .env or other configuration files.
- Running arbitrary system commands under the web server user context.

This issue is Critical as it allows a low-privilege authenticated user to fully compromise the application and underlying server.

### Patches
This vulnerability was patched by https://github.com/Paymenter/Paymenter/commit/87c3db42282ada1e3cda54b9a01f846926c0669b and was released under the [v1.2.11](https://github.com/Paymenter/Paymenter/releases/tag/v1.2.11) tag without any other code modifications compared to v1.2.10.

### Work arounds
If upgrading is not immediately possible, administrators can mitigate this vulnerability with one or more of the following measures:

- Updating nginx config to download attachments instead of executing them:
```
location ^~ /storage/ {
    types { }
    default_type application/octet-stream;
    add_header X-Content-Type-Options nosniff;
    try_files $uri =404;
}
```
- Disallow access to /storage/ fully using a WAF such as Cloudflare

These workarounds significantly reduce risk, but the only guaranteed resolution is upgrading to v1.2.11 or later.

## References
- https://github.com/Paymenter/Paymenter/security/advisories/GHSA-5pm9-r2m8-rcmj
- https://nvd.nist.gov/vuln/detail/CVE-2025-58048
- https://github.com/Paymenter/Paymenter/commit/87c3db42282ada1e3cda54b9a01f846926c0669b
- https://github.com/Paymenter/Paymenter
- https://github.com/Paymenter/Paymenter/releases/tag/v1.2.11
