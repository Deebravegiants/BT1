# [H] CVE-2018-16398

## Summary
Severity: High
Advisory: CVE-2018-16398
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-09-03
Source: https://osv.dev/vulnerability/CVE-2018-16398
Type: osv

## Details
In Twistlock AuthZ Broker 0.1, regular expressions are mishandled, as demonstrated by containers/aa/pause?aaa=\/start to bypass a policy in which "docker start" is allowed but "docker pause" is not allowed.

## References
- https://github.com/twistlock/authz/issues/50
- https://github.com/twistlock/authz/issues/51
