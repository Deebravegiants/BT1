# [H] CVE-2016-10002

## Summary
Severity: High
Advisory: CVE-2016-10002
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/CVE-2016-10002
Type: osv

## Details
Incorrect processing of responses to If-None-Modified HTTP conditional requests in Squid HTTP Proxy 3.1.10 through 3.1.23, 3.2.0.3 through 3.5.22, and 4.0.1 through 4.0.16 leads to client-specific Cookie data being leaked to other clients. Attack requests can easily be crafted by a client to probe a cache for this information.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0182.html
- http://rhn.redhat.com/errata/RHSA-2017-0183.html
- http://www.debian.org/security/2016/dsa-3745
- http://www.securityfocus.com/bid/94953
- http://www.securitytracker.com/id/1037513
- http://www.openwall.com/lists/oss-security/2016/12/18/1
- http://www.squid-cache.org/Advisories/SQUID-2016_11.txt
