# [H] Buffer overflow due to use of `strcpy` in `performRtspHandshake`

## Summary
Severity: High
Advisory: CVE-2023-42800
Aliases: GHSA-4927-23jw-rq62
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/CVE-2023-42800
Type: osv

## Details
Moonlight-common-c contains the core GameStream client code shared between Moonlight clients. Moonlight-common-c is vulnerable to buffer overflow starting in commit 50c0a51b10ecc5b3415ea78c21d96d679e2288f9 due to unmitigated usage of unsafe C functions and improper bounds checking. A malicious game streaming server could exploit a buffer overflow vulnerability to crash a moonlight client, or achieve remote code execution (RCE) on the client (with insufficient exploit mitigations or if mitigations can be bypassed). The bug was addressed in commit 24750d4b748fefa03d09fcfd6d45056faca354e0.

## References
- https://github.com/moonlight-stream/moonlight-common-c/blob/2bb026c763fc18807d7e4a93f918054c488f84e1/src/RtspConnection.c#L796
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42800.json
- https://github.com/moonlight-stream/moonlight-common-c/security/advisories/GHSA-4927-23jw-rq62
- https://nvd.nist.gov/vuln/detail/CVE-2023-42800
- https://github.com/moonlight-stream/moonlight-common-c/commit/24750d4b748fefa03d09fcfd6d45056faca354e0
- https://github.com/moonlight-stream/moonlight-common-c/commit/50c0a51b10ecc5b3415ea78c21d96d679e2288f9
