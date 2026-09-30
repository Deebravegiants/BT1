# [H] CVE-2019-5739

## Summary
Severity: High
Advisory: CVE-2019-5739
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-28
Source: https://osv.dev/vulnerability/CVE-2019-5739
Type: osv

## Details
Keep-alive HTTP and HTTPS connections can remain open and inactive for up to 2 minutes in Node.js 6.16.0 and earlier. Node.js 8.0.0 introduced a dedicated server.keepAliveTimeout which defaults to 5 seconds. The behavior in Node.js 6.16.0 and earlier is a potential Denial of Service (DoS) attack vector. Node.js 6.17.0 introduces server.keepAliveTimeout and the 5-second default.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00046.html
- https://nodejs.org/en/blog/vulnerability/february-2019-security-releases/
- https://security.gentoo.org/glsa/202003-48
- https://security.netapp.com/advisory/ntap-20190502-0008/
