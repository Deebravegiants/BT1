# [H] CVE-2024-51094

## Summary
Severity: High
Advisory: CVE-2024-51094
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-11-12
Source: https://osv.dev/vulnerability/CVE-2024-51094
Type: osv

## Details
An issue in Snipe-IT v.7.0.13 build 15514 allows a low-privileged attacker to modify their profile name and inject a malicious payload into the "Name" field. When an administrator later accesses the People Management page, exports the data as a CSV file, and opens it, the injected payload will be executed, allowing the attacker to exfiltrate internal system data from the CSV file to a remote server.

## References
- https://gist.githubusercontent.com/Tommywarren/b3a6c6ae5a93dd67c863313f71f53a76/raw/ddff8cbbab5179f680ba3f5e94fc080575ad8913/CVE-2024-51094
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51094.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-51094
