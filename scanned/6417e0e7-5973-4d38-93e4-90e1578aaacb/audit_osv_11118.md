# [H] CVE-2017-6201

## Summary
Severity: High
Advisory: CVE-2017-6201
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/CVE-2017-6201
Type: osv

## Details
A Server Side Request Forgery vulnerability exists in the install app process in Sandstorm before build 0.203. A remote attacker may exploit this issue by providing a URL. It could bypass access control such as firewalls that prevent the attackers from accessing the URLs directly.

## References
- https://sandstorm.io/news/2017-03-02-security-review
- https://github.com/sandstorm-io/sandstorm/commit/164997fb958effbc90c5328c166706280a84aaa1
- https://devco.re/blog/2018/01/26/Sandstorm-Security-Review-CVE-2017-6200-en/
