# [H] CVE-2021-30070

## Summary
Severity: High
Advisory: CVE-2021-30070
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-08-18
Source: https://osv.dev/vulnerability/CVE-2021-30070
Type: osv

## Details
An issue was discovered in HestiaCP before v1.3.5. Attackers are able to arbitrarily install packages due to values taken from the pgk [] parameter in the update request being transmitted to the operating system's package manager.

## References
- https://github.com/hestiacp/hestiacp/commit/27556a9a43aeaf308b33be224c2e70f2011574e6
- https://github.com/hestiacp/hestiacp/commit/9a1fccd37f2842fdf96ffb48895c4bfa9788c469
