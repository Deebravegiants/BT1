# [M] CVE-2024-46540

## Summary
Severity: Medium
Advisory: CVE-2024-46540
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L)
Published: 2024-09-30
Source: https://osv.dev/vulnerability/CVE-2024-46540
Type: osv

## Details
A remote code execution (RCE) vulnerability in the component /admin/store.php of Emlog Pro before v2.3.15 allows attackers to use remote file downloads and self-extract fucntions to upload webshells to the target server, thereby obtaining system privileges.

## References
- https://gist.github.com/microvorld/1c1ef9c3390a5d88a5ede9f9424a8bd2
- https://github.com/microvorld/CVE-2024/blob/main/emlog.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46540.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46540
- https://github.com/emlog/emlog
