# [M] Chamilo: Potential unauthenticated blind SSRF via openid function

## Summary
Severity: Medium
Advisory: CVE-2024-50337
Aliases: GHSA-rp2w-g734-jf8h
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2024-50337
Type: osv

## Details
Chamilo is a learning management system. Prior to version 1.11.28, the OpenId function allows anyone to send requests to any URL on server's behalf, which results in unauthenticated blind SSRF. This issue has been patched in version 1.11.28.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.28
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50337.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-rp2w-g734-jf8h
- https://nvd.nist.gov/vuln/detail/CVE-2024-50337
- https://github.com/chamilo/chamilo-lms/commit/43a9bd1fb8b3f57e7935a6a6bc48975e2063b01b
