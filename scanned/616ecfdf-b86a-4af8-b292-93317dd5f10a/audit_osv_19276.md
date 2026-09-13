# [H] CVE-2020-9483

## Summary
Severity: High
Advisory: CVE-2020-9483
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-30
Source: https://osv.dev/vulnerability/CVE-2020-9483
Type: osv

## Details
**Resolved** When use H2/MySQL/TiDB as Apache SkyWalking storage, the metadata query through GraphQL protocol, there is a SQL injection vulnerability, which allows to access unpexcted data. Apache SkyWalking 6.0.0 to 6.6.0, 7.0.0 H2/MySQL/TiDB storage implementations don't use the appropriate way to set SQL parameters.

## References
- https://github.com/apache/skywalking/pull/4639
