# [H] Kimai contains a SameSite cookie vulnerability

## Summary
Severity: High
Advisory: GHSA-cv8h-r7r5-vwj9
CVE: CVE-2023-53957
CWE: CWE-1275
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-19
Source: https://github.com/advisories/GHSA-cv8h-r7r5-vwj9
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0

## Details
Kimai 1.30.10 contains a SameSite cookie vulnerability that allows attackers to steal user session cookies through malicious exploitation. Attackers can trick victims into executing a crafted PHP script that captures and writes session cookie information to a file, enabling potential session hijacking.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-53957
- https://github.com/kimai/kimai
- https://www.exploit-db.com/exploits/51278
- https://www.vulncheck.com/advisories/kimai-samesite-cookie-vulnerability-session-hijacking
