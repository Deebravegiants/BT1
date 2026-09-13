# [M] CVE-2016-8738

## Summary
Severity: Medium
Advisory: CVE-2016-8738
Aliases: GHSA-86vq-8qhc-5rqw
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-20
Source: https://osv.dev/vulnerability/CVE-2016-8738
Type: osv

## Details
In Apache Struts 2.5 through 2.5.5, if an application allows entering a URL in a form field and the built-in URLValidator is used, it is possible to prepare a special URL which will be used to overload server process when performing validation of the URL.

## References
- http://www.securityfocus.com/bid/94657
- https://security.netapp.com/advisory/ntap-20180629-0003/
- https://struts.apache.org/docs/s2-044.html
