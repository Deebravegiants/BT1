# [H] BIT-guacamole-2021-43999

## Summary
Severity: High
Advisory: BIT-guacamole-2021-43999
Aliases: BIT-guacamole-server-2021-43999, CVE-2021-43999
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-guacamole-2021-43999
Type: osv

## Affected
- Bitnami: `guacamole` — affected >=1.3.0

## Details
Apache Guacamole 1.2.0 and 1.3.0 do not properly validate responses received from a SAML identity provider. If SAML support is enabled, this may allow a malicious user to assume the identity of another Guacamole user.

## References
- http://www.openwall.com/lists/oss-security/2022/01/11/7
- https://lists.apache.org/thread/4dt9h5mo4o9rxlgxm3rp8wfqdtdjn2z9
