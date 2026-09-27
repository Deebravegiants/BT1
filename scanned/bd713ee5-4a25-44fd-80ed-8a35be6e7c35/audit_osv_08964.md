# [M] CVE-2016-7099

## Summary
Severity: Medium
Advisory: CVE-2016-7099
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-10-10
Source: https://osv.dev/vulnerability/CVE-2016-7099
Type: osv

## Details
The tls.checkServerIdentity function in Node.js 0.10.x before 0.10.47, 0.12.x before 0.12.16, 4.x before 4.6.0, and 6.x before 6.7.0 does not properly handle wildcards in name fields of X.509 certificates, which allows man-in-the-middle attackers to spoof servers via a crafted certificate.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00013.html
- http://rhn.redhat.com/errata/RHSA-2017-0002.html
- http://www.securityfocus.com/bid/93191
- https://github.com/nodejs/node/commit/743f0c916469f3129dfae406fa104dc46782e20b
- https://nodejs.org/en/blog/vulnerability/september-2016-security-releases/
