# [C] WBCE CMS 1.5.2 - Remote Code Execution (RCE) (Authenticated)

## Summary
Severity: Critical
Advisory: CVE-2022-50936
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2022-50936
Type: osv

## Details
WBCE CMS version 1.5.2 contains an authenticated remote code execution vulnerability that allows attackers to upload malicious droplets through the admin panel. Authenticated attackers can exploit the droplet upload functionality in the admin tools to create and execute arbitrary PHP code by crafting a specially designed zip file payload.

## References
- https://wbce.org/
- https://wbce.org/de/downloads/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50936.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50936
- https://www.vulncheck.com/advisories/wbce-cms-remote-code-execution-rce-authenticated
- https://github.com/WBCE/WBCE_CMS
- https://www.exploit-db.com/exploits/50707
