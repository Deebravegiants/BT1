# [M] CVE-2019-7351

## Summary
Severity: Medium
Advisory: CVE-2019-7351
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2019-7351
Type: osv

## Details
Log Injection exists in ZoneMinder through 1.32.3, as an attacker can entice the victim to visit a specially crafted link, which in turn will inject a custom Log message provided by the attacker in the 'log' view page, as demonstrated by the message=User%20'admin'%20Logged%20in value.

## References
- https://github.com/ZoneMinder/zoneminder/issues/2466
