# [H] CVE-2021-42194

## Summary
Severity: High
Advisory: CVE-2021-42194
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-20
Source: https://osv.dev/vulnerability/CVE-2021-42194
Type: osv

## Details
The wechat_return function in /controller/Index.php of EyouCms V1.5.4-UTF8-SP3 passes the user's input directly into the simplexml_ load_ String function, which itself does not prohibit external entities, triggering a XML external entity (XXE) injection vulnerability.

## References
- https://github.com/eyoucms/eyoucms/issues/19
