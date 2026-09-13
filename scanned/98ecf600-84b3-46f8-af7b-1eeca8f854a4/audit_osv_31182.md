# [C] dizqueTV 1.5.3 Remote Code Execution via FFMPEG Executable Path

## Summary
Severity: Critical
Advisory: CVE-2024-58286
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-11
Source: https://osv.dev/vulnerability/CVE-2024-58286
Type: osv

## Details
dizqueTV 1.5.3 contains a remote code execution vulnerability that allows attackers to inject arbitrary commands through the FFMPEG Executable Path settings. Attackers can modify the executable path with shell commands to read system files like /etc/passwd by exploiting improper input validation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58286.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58286
- https://www.vulncheck.com/advisories/dizquetv-remote-code-execution-via-ffmpeg-executable-path
- https://github.com/vexorian/dizquetv
- https://www.exploit-db.com/exploits/52079
