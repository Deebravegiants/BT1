# [C] CVE-2021-3331

## Summary
Severity: Critical
Advisory: CVE-2021-3331
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-27
Source: https://osv.dev/vulnerability/CVE-2021-3331
Type: osv

## Details
WinSCP before 5.17.10 allows remote attackers to execute arbitrary programs when the URL handler encounters a crafted URL that loads session settings. (For example, this is exploitable in a default installation in which WinSCP is the handler for sftp:// URLs.)

## References
- https://winscp.net/eng/docs/history#5.17.10
- https://winscp.net/eng/docs/rawsettings
- https://github.com/winscp/winscp/commit/faa96e8144e6925a380f94a97aa382c9427f688d
- https://winscp.net/tracker/1943
