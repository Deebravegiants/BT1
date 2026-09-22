# [H] CVE-2018-20684

## Summary
Severity: High
Advisory: CVE-2018-20684
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-01-10
Source: https://osv.dev/vulnerability/CVE-2018-20684
Type: osv

## Details
In WinSCP before 5.14 beta, due to missing validation, the scp implementation would accept arbitrary files sent by the server, potentially overwriting unrelated files. This affects TSCPFileSystem::SCPSink in core/ScpFileSystem.cpp.

## References
- https://www.oracle.com/security-alerts/cpujan2020.html
- http://www.securityfocus.com/bid/106526
- https://sintonen.fi/advisories/scp-client-multiple-vulnerabilities.txt
- https://winscp.net/eng/docs/history
- https://github.com/winscp/winscp/commit/49d876f2c5fc00bcedaa986a7cf6dedd6bf16f54
- https://winscp.net/tracker/1675
