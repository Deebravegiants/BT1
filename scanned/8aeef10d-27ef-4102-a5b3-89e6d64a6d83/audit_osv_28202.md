# [H] TarSlip Vulnerability in deepjavalibrary/djl

## Summary
Severity: High
Advisory: CVE-2024-2914
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-2914
Type: osv

## Details
A TarSlip vulnerability exists in the deepjavalibrary/djl, affecting version 0.26.0 and fixed in version 0.27.0. This vulnerability allows an attacker to manipulate file paths within tar archives to overwrite arbitrary files on the target system. Exploitation of this vulnerability could lead to remote code execution, privilege escalation, data theft or manipulation, and denial of service. The vulnerability is due to improper validation of file paths during the extraction of tar files, as demonstrated in multiple occurrences within the library's codebase, including but not limited to the files_util.py and extract_imagenet.py scripts.

## References
- https://huntr.com/bounties/b064bd2f-bf6e-4fc0-898e-7d02a9b97e24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2914.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2914
- https://github.com/deepjavalibrary/djl/commit/5235be508cec9e8cb6f496a4ed2fa40e4f62c370
