# [H] Zed: Zed IDE Arbitrary Code Execution via untrusted repository with poisoned .git/config

## Summary
Severity: High
Advisory: CVE-2026-44465
Aliases: GHSA-fj2r-rmw6-h222
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-44465
Type: osv

## Details
Zed is a code editor. Prior to 0.227.1, Zed IDE executes arbitrary commands when opening a folder with a malicious .git/config file that abuses the core.fsmonitor Git configuration option. This allows an attacker to achieve Remote Code Execution (RCE) when a victim open a folder in untrusted mode. This vulnerability is fixed in 0.227.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44465.json
- https://github.com/zed-industries/zed/security/advisories/GHSA-fj2r-rmw6-h222
- https://nvd.nist.gov/vuln/detail/CVE-2026-44465
