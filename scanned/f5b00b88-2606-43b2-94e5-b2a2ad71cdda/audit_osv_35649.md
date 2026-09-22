# [C] CVE-2026-12116

## Summary
Severity: Critical
Advisory: CVE-2026-12116
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-12116
Type: osv

## Details
A vulnerability in the Xerte Online Tools allows for RCE through the antivirus binary path in the tools server settings, which can be changed to a PHP interpreter, allowing an attacker to upload PHP data that will then be executed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12116.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-12116
- https://github.com/thexerteproject/xerteonlinetoolkits/issues/1543
- https://github.com/thexerteproject/xerteonlinetoolkits/commit/8ef20628f80bd88bd1fe3e5844a9116a910086b7
- https://www.xerte.org.uk/index.php/en/news/blog/80-news/364-xerte-3-14-and-3-15-important-security-update
