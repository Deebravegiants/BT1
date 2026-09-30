# [C] reNgine 2.2.0 Authenticated Command Injection via Scan Engine Configuration

## Summary
Severity: Critical
Advisory: CVE-2024-58287
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-11
Source: https://osv.dev/vulnerability/CVE-2024-58287
Type: osv

## Details
reNgine 2.2.0 contains a command injection vulnerability in the nmap_cmd parameter of scan engine configuration that allows authenticated attackers to execute arbitrary commands. Attackers can modify the nmap_cmd parameter with malicious base64-encoded payloads to achieve remote code execution during scan engine configuration.

## References
- https://rengine.wiki/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58287.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58287
- https://www.vulncheck.com/advisories/rengine-authenticated-command-injection-via-scan-engine-configuration
- https://github.com/yogeshojha/rengine
- https://www.exploit-db.com/exploits/52081
