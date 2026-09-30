# [H] Jellyfin Vulnerable to Argument Injection in FFmpeg

## Summary
Severity: High
Advisory: CVE-2025-31499
Aliases: GHSA-2c3c-r7gp-q32m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-31499
Type: osv

## Details
Jellyfin is an open source self hosted media server. Versions before 10.10.7 are vulnerable to argument injection in FFmpeg. This can be leveraged to possibly achieve remote code execution by anyone with credentials to a low-privileged user. This vulnerability was previously reported in CVE-2023-49096 and patched in version 10.8.13, but the patch can be bypassed. The original fix sanitizes some parameters to make injection impossible, but certain unsanitized parameters can still be used for argument injection. The same unauthenticated endpoints are vulnerable: /Videos/<itemId>/stream and /Videos/<itemId>/stream.<container>, likely alongside similar endpoints in AudioController. This argument injection can be exploited to achieve arbitrary file write, leading to possible remote code execution through the plugin system. While the unauthenticated endpoints are vulnerable, a valid itemId is required for exploitation and any authenticated attacker could easily retrieve a valid itemId to make the exploit work. This vulnerability is patched in version 10.10.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31499.json
- https://github.com/jellyfin/jellyfin/security/advisories/GHSA-2c3c-r7gp-q32m
- https://nvd.nist.gov/vuln/detail/CVE-2025-31499
- https://github.com/jellyfin/jellyfin/commit/79f3ce53257c5291887cd52d8ac735b5252c9a97
