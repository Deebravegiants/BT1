# [H] Buffer overflow due to use of `strcpy` in `parseUrlAddrFromRtspUrlString`

## Summary
Severity: High
Advisory: CVE-2023-42799
Aliases: GHSA-r8cf-45f4-vf8m
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/CVE-2023-42799
Type: osv

## Details
Moonlight-common-c contains the core GameStream client code shared between Moonlight clients. Moonlight-common-c is vulnerable to buffer overflow starting in commit 50c0a51b10ecc5b3415ea78c21d96d679e2288f9 due to unmitigated usage of unsafe C functions and improper bounds checking. A malicious game streaming server could exploit a buffer overflow vulnerability to crash a moonlight client, or achieve remote code execution (RCE) on the client (with insufficient exploit mitigations or if mitigations can be bypassed). The bug was addressed in commit 02b7742f4d19631024bd766bd2bb76715780004e.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42799.json
- https://github.com/moonlight-stream/moonlight-common-c/security/advisories/GHSA-r8cf-45f4-vf8m
- https://nvd.nist.gov/vuln/detail/CVE-2023-42799
- https://github.com/moonlight-stream/moonlight-common-c/commit/02b7742f4d19631024bd766bd2bb76715780004e
- https://github.com/moonlight-stream/moonlight-common-c/commit/50c0a51b10ecc5b3415ea78c21d96d679e2288f9
