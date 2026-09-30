# [H] FastGPT: S3 presign/read handlers do not bind the object key to the caller's team (cross-team file disclosure)

## Summary
Severity: High
Advisory: CVE-2026-55418
Aliases: GHSA-6rxv-p43w-mmx5
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-55418
Type: osv

## Details
FastGPT is an open source AI knowledge base platform. Prior to v4.15.0-beta5, two FastGPT file handlers authorize an unrelated resource and then sign or read an S3 object using a key taken directly from the request, without checking that the key belongs to the caller's team. Because S3 object keys are global within the bucket and carry the tenant id only as a path segment, an attacker can supply another team's key and obtain its file contents through the chat-file presign endpoint or dataset preview endpoint. This issue is fixed in version v4.15.0-beta5.

## References
- https://github.com/labring/FastGPT/releases/tag/v4.15.0-beta5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55418.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-6rxv-p43w-mmx5
- https://nvd.nist.gov/vuln/detail/CVE-2026-55418
- https://github.com/labring/FastGPT/commit/decb6d2fb1417fb9e2bca145d2dcc9cbcf06396c
- https://github.com/labring/FastGPT/pull/7104
