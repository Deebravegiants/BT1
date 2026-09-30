# [C] MCMS allows arbitrary file uploads in the ueditor component

## Summary
Severity: Critical
Advisory: GHSA-3922-2r6r-r4fv
CVE: CVE-2025-29287
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-21
Source: https://github.com/advisories/GHSA-3922-2r6r-r4fv
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0 <5.4.4

## Details
An arbitrary file upload vulnerability in the ueditor component of MCMS v5.4.3 allows attackers to execute arbitrary code via uploading a crafted file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-29287
- https://gist.github.com/erdan111/38dcb5150b523436fe01249b2542f02f#file-cve-2025-29287
- https://gitee.com/mingSoft/MCMS/commit/17679d8fae3df2b433478829b01ab05a56ffdbc8
- https://gitee.com/mingSoft/MCMS/issues/IBOOTX
- https://github.com/ming-soft/MCMS
