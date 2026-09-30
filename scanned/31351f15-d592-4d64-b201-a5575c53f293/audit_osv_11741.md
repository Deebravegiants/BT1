# [H] CVE-2017-9454

## Summary
Severity: High
Advisory: CVE-2017-9454
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-18
Source: https://osv.dev/vulnerability/CVE-2017-9454
Type: osv

## Details
Buffer overflow in the ares_parse_a_reply function in the embedded ares library in ReSIProcate before 1.12.0 allows remote attackers to cause a denial of service (out-of-bounds-read) via a crafted DNS response.

## References
- https://list.resiprocate.org/archive/resiprocate-users/msg02700.html
- https://github.com/resiprocate/resiprocate/commit/d67a9ca6fd06ca65d23e313bdbad1ef4dd3aa0df
