# [H] OpenCTI's lack of Rate Limit lead to OTP brute forcing

## Summary
Severity: High
Advisory: CVE-2024-45404
Aliases: GHSA-hg56-r6hh-56j7, PYSEC-2024-297
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-45404
Type: osv

## Details
OpenCTI is an open-source cyber threat intelligence platform. In versions below 6.2.18, because the function to limit the rate of OTP does not exist, an attacker with valid credentials or a malicious user who commits internal fraud can break through the two-factor authentication and hijack the account. This is because the otpLogin mutation does not implement One Time Password rate limiting. As of time of publication, it is unknown whether a patch is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45404.json
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-hg56-r6hh-56j7
- https://nvd.nist.gov/vuln/detail/CVE-2024-45404
