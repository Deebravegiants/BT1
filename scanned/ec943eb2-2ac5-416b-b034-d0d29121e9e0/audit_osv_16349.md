# [H] CVE-2019-5737

## Summary
Severity: High
Advisory: CVE-2019-5737
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-28
Source: https://osv.dev/vulnerability/CVE-2019-5737
Type: osv

## Details
In Node.js including 6.x before 6.17.0, 8.x before 8.15.1, 10.x before 10.15.2, and 11.x before 11.10.1, an attacker can cause a Denial of Service (DoS) by establishing an HTTP or HTTPS connection in keep-alive mode and by sending headers very slowly. This keeps the connection and associated resources alive for a long period of time. Potential attacks are mitigated by the use of a load balancer or other proxy layer. This vulnerability is an extension of CVE-2018-12121, addressed in November and impacts all active Node.js release lines including 6.x before 6.17.0, 8.x before 8.15.1, 10.x before 10.15.2, and 11.x before 11.10.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00046.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00059.html
- https://access.redhat.com/errata/RHSA-2019:1821
- https://nodejs.org/en/blog/vulnerability/february-2019-security-releases/
- https://security.gentoo.org/glsa/202003-48
- https://security.netapp.com/advisory/ntap-20190502-0008/
