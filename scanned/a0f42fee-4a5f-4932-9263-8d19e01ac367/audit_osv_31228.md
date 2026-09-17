# [C] Arbitrary File Overwrite and Data Exfiltration in aimhubio/aim

## Summary
Severity: Critical
Advisory: CVE-2024-6396
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-6396
Type: osv

## Details
A vulnerability in the `_backup_run` function in aimhubio/aim version 3.19.3 allows remote attackers to overwrite any file on the host server and exfiltrate arbitrary data. The vulnerability arises due to improper handling of the `run_hash` and `repo.path` parameters, which can be manipulated to create and write to arbitrary file paths. This can lead to denial of service by overwriting critical system files, loss of private data, and potential remote code execution.

## References
- https://huntr.com/bounties/c1b17afd-4656-47bb-8310-686a9e1b04a0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6396.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6396
