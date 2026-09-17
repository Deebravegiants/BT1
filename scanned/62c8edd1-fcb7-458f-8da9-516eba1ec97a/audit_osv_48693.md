# [M] CVE-2018-11469

## Summary
Severity: Medium
Advisory: CVE-2018-11469
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-05-25
Source: https://osv.dev/vulnerability/CVE-2018-11469
Type: osv

## Details
Incorrect caching of responses to requests including an Authorization header in HAProxy 1.8.0 through 1.8.9 (if cache enabled) allows attackers to achieve information disclosure via an unauthenticated remote request, related to the proto_http.c check_request_for_cacheability function.

## References
- https://git.haproxy.org/?p=haproxy-1.8.git%3Ba=commit%3Bh=17514045e5d934dede62116216c1b016fe23dd06
- http://www.securityfocus.com/bid/104347
- https://access.redhat.com/errata/RHSA-2019:1436
- https://usn.ubuntu.com/3663-1/
