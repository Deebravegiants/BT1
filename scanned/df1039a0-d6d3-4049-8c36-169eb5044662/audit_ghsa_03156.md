# [H] Improper Certificate Validation in EM-HTTP-Request

## Summary
Severity: High
Advisory: GHSA-q27f-v3r6-9v77
CVE: CVE-2020-13482
CWE: CWE-295
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-q27f-v3r6-9v77
Type: github-advisory

## Affected
- RubyGems: `em-http-request` — affected >=0 <1.1.6

## Details
EM-HTTP-Request 1.1.5 uses the library eventmachine in an insecure way that allows an attacker to perform a man-in-the-middle attack against users of the library. The hostname in a TLS server certificate is not verified.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13482
- https://github.com/igrigorik/em-http-request/issues/339
- https://github.com/igrigorik/em-http-request/commit/e5fa144f8d21050dd1fc15a4dc8aa34ac6f30602
- https://github.com/advisories/GHSA-q27f-v3r6-9v77
- https://github.com/igrigorik/em-http-request
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/em-http-request/CVE-2020-13482.yml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MKYP5TR5NTVVDX5R4HCNNH2OQR7M4X3J
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z32PUJA6RGBZ3TKSOTGUXZ45662S3MVF
- https://securitylab.github.com/advisories/GHSL-2020-094-igrigorik-em-http-request
