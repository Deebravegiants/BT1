# [C] CVE-2025-22275

## Summary
Severity: Critical
Advisory: CVE-2025-22275
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N)
Published: 2025-01-03
Source: https://osv.dev/vulnerability/CVE-2025-22275
Type: osv

## Details
iTerm2 3.5.6 through 3.5.10 before 3.5.11 sometimes allows remote attackers to obtain sensitive information from terminal commands by reading the /tmp/framer.txt file. This can occur for certain it2ssh and SSH Integration configurations, during remote logins to hosts that have a common Python installation.

## References
- https://gitlab.com/gnachman/iterm2/-/wikis/SSH-Integration-Information-Leak
- https://iterm2.com/downloads/stable/iTerm2-3_5_11.changelog
- https://news.ycombinator.com/item?id=42579472
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22275.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22275
