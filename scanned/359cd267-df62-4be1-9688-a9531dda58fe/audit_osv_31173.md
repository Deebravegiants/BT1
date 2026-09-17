# [M] File Overwrite Vulnerability in gaizhenbiao/chuanhuchatgpt

## Summary
Severity: Medium
Advisory: CVE-2024-5823
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-5823
Type: osv

## Details
A file overwrite vulnerability exists in gaizhenbiao/chuanhuchatgpt versions <= 20240410. This vulnerability allows an attacker to gain unauthorized access to overwrite critical configuration files within the system. Exploiting this vulnerability can lead to unauthorized changes in system behavior or security settings. Additionally, tampering with these configuration files can result in a denial of service (DoS) condition, disrupting normal system operation.

## References
- https://huntr.com/bounties/ca361701-7d68-4df6-8da0-caad4b85b9ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5823.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5823
- https://github.com/gaizhenbiao/chuanhuchatgpt/commit/720c23d755a4a955dcb0a54e8c200a2247a27f8b
