# [C] Cherry Studio RCE via SearchService nodeIntegration Misconfiguration

## Summary
Severity: Critical
Advisory: CVE-2026-40501
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-40501
Type: osv

## Details
Cherry Studio versions 1.2.2 through 1.9.12, fixed in commit 1518530, contain a remote code execution vulnerability in SearchService that allows remote attackers to execute arbitrary code by delivering malicious JavaScript through controlled search provider content loaded into an Electron BrowserWindow configured with nodeIntegration enabled and contextIsolation disabled. Attackers who control a search engine provider, individual search result pages, or provider settings pages can execute JavaScript with full Node.js privileges, gaining access to fs, child_process, os, and process.env under the operating-system account of the Cherry Studio process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40501.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40501
- https://www.vulncheck.com/advisories/cherry-studio-rce-via-searchservice-nodeintegration-misconfiguration
- https://github.com/CherryHQ/cherry-studio/commit/151853035e8e417a51559ebfc243eda98361a882
- https://github.com/CherryHQ/cherry-studio
- https://gist.github.com/Mundi-Xu/99af1b08275fd437cfb79bfe481e68b7
