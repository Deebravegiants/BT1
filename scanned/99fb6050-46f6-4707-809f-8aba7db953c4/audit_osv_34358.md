# [C] Dyad Vulnerable to Remote Code Execution via Top-level Navigation in Preview Window

## Summary
Severity: Critical
Advisory: CVE-2025-58766
Aliases: GHSA-7fxm-c5xx-7vpq
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2025-58766
Type: osv

## Details
Dyad is a local AI app builder. A critical security vulnerability has been discovered that affected Dyad v0.19.0 and earlier versions that allows attackers to execute arbitrary code on users' systems. The vulnerability affects the application's preview window functionality and can bypass Docker container protections.  An attacker can craft web content that automatically executes when the preview loads. The malicious content can break out of the application's security boundaries and gain control of the system. This has been fixed in Dyad v0.20.0 and later.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58766.json
- https://github.com/dyad-sh/dyad/security/advisories/GHSA-7fxm-c5xx-7vpq
- https://nvd.nist.gov/vuln/detail/CVE-2025-58766
- https://github.com/dyad-sh/dyad/commit/1c0255ab126d3b38ae9e78b17cdab9a07e5f0185
- https://github.com/dyad-sh/dyad/commit/ebcf89ee6cead83a33add5ef1e19c8d4f9b4ce9b
