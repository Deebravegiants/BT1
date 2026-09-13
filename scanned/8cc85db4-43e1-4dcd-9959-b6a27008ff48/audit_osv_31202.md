# [H] Arbitrary Folder Creation in gaizhenbiao/chuanhuchatgpt

## Summary
Severity: High
Advisory: CVE-2024-6037
Aliases: PYSEC-2024-317
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-10
Source: https://osv.dev/vulnerability/CVE-2024-6037
Type: osv

## Details
A vulnerability in gaizhenbiao/chuanhuchatgpt version 20240410 allows an attacker to create arbitrary folders at any location on the server, including the root directory (C: dir). This can lead to uncontrolled resource consumption, resulting in resource exhaustion, denial of service (DoS), server unavailability, and potential data loss or corruption.

## References
- https://huntr.com/bounties/eca6904f-f9fd-40c8-9e85-96f54daf405e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6037.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6037
- https://github.com/gaizhenbiao/chuanhuchatgpt/commit/71cb89c4c948dae5aaa0ae64b98f98e3965bdb37
