# [M] CVE-2020-12105

## Summary
Severity: Medium
Advisory: CVE-2020-12105
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-23
Source: https://osv.dev/vulnerability/CVE-2020-12105
Type: osv

## Details
OpenConnect through 8.08 mishandles negative return values from X509_check_ function calls, which might assist attackers in performing man-in-the-middle attacks.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00039.html
- https://gitlab.com/openconnect/openconnect/-/merge_requests/96
- https://security.gentoo.org/glsa/202006-15
