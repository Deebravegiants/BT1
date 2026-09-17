# [C] CVE-2017-6199

## Summary
Severity: Critical
Advisory: CVE-2017-6199
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/CVE-2017-6199
Type: osv

## Details
A remote attacker could bypass the Sandstorm organization restriction before build 0.203 via a comma in an email-address field.

## References
- https://github.com/sandstorm-io/sandstorm/blob/v0.202/shell/packages/sandstorm-db/db.js#L1112
- https://sandstorm.io/news/2017-03-02-security-review
- https://github.com/sandstorm-io/sandstorm/commit/37bd9a7f4eb776cdc2d3615f0bfea1254b66f59d
- https://devco.re/blog/2018/01/26/Sandstorm-Security-Review-CVE-2017-6200-en/
