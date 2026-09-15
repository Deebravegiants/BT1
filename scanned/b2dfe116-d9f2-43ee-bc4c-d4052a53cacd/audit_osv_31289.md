# [H] Arbitrary File Read via Insufficient Validation in gaizhenbiao/chuanhuchatgpt

## Summary
Severity: High
Advisory: CVE-2024-7962
Aliases: PYSEC-2024-112
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-7962
Type: osv

## Details
An arbitrary file read vulnerability exists in gaizhenbiao/chuanhuchatgpt version 20240628 due to insufficient validation when loading prompt template files. An attacker can read any file that matches specific criteria using an absolute path. The file must not have a .json extension and, except for the first line, every other line must contain commas. This vulnerability allows reading parts of format-compliant files, including code and log files, which may contain highly sensitive information such as account credentials.

## References
- https://huntr.com/bounties/83f0a8e1-490c-49e7-b334-02125ee0f1b1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7962.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7962
- https://github.com/gaizhenbiao/chuanhuchatgpt/commit/2836fd1db3efcd5ede63c0e7fbbdf677730dbb51
