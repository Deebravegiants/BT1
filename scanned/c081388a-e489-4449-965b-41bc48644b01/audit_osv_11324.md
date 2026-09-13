# [M] CVE-2017-7395

## Summary
Severity: Medium
Advisory: CVE-2017-7395
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-01
Source: https://osv.dev/vulnerability/CVE-2017-7395
Type: osv

## Details
In TigerVNC 1.7.1 (SMsgReader.cxx SMsgReader::readClientCutText), by causing an integer overflow, an authenticated client can crash the server.

## References
- http://www.securityfocus.com/bid/97305
- https://access.redhat.com/errata/RHSA-2017:2000
- https://security.gentoo.org/glsa/201801-13
- https://github.com/TigerVNC/tigervnc/pull/436
- https://github.com/TigerVNC/tigervnc/pull/436/commits/bf3bdac082978ca32895a4b6a123016094905689
