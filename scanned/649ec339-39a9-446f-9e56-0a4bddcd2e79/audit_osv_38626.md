# [C] Tautulli Vulnerable to Unauthenticated/Authenticated Remote Code Execution via Newsletter Custom Template Directory

## Summary
Severity: Critical
Advisory: CVE-2026-41065
Aliases: GHSA-68qx-mcf5-3jcp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-41065
Type: osv

## Details
Tautulli is a Python based monitoring and tracking tool for Plex Media Server. Versions prior to 2.17.1 are vulnerable to remote code execution via the newsletter custom template directory feature. On a fresh install before the setup wizard is completed, all management endpoints are completely unauthenticated. An attacker can create a newsletter agent, point the custom template directory to an attacker-controlled SMB share serving a malicious Mako template, and trigger execution via the newsletter render endpoint, all with zero credentials and no local access to the target system. On a completed install with credentials configured, the same chain is exploitable by any admin. Version 2.17.1 fixes the issue.

## References
- https://github.com/Tautulli/Tautulli/releases/tag/v2.17.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41065.json
- https://github.com/Tautulli/Tautulli/security/advisories/GHSA-68qx-mcf5-3jcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-41065
