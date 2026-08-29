# [M] cURL / libcURL - CVE-2016-8624 invalid URL parsing with '#'

## Summary
Severity: Medium (CVSS 6.5)
Program: Internet Bug Bounty
Weakness: Server-Side Request Forgery (SSRF)
Reporter: fms
State: resolved
Disclosed: 2018-01-11T20:41:15.192Z
CVE: CVE-2016-8624
Source: https://hackerone.com/reports/180434

## Details
invalid URL parsing with '#'
============================

Project cURL Security Advisory, November 2, 2016 -
[Permalink] https://curl.haxx.se/docs/adv_20161102J.html

VULNERABILITY
-------------

curl doesn't parse the authority component of the URL correctly when the host
name part ends with a '#' character, and could instead be tricked into
connecting to a different host. This may have security implications if you for
example use a URL parser that follows the RFC to check for allowed domains
before using curl to request them.

Passing in `http://example.com#@evil.com/x.txt` would wrongly make curl send a
request to evil.com while your browser would connect to example.com given the
same URL.

The problem exists for most protocol schemes.

We are not aware of any exploit of this flaw.

INFO
----

The Common Vulnerabilities and Exposures (CVE) project has assigned the name
CVE-2016-8624 to this issue.

AFFECTED VERSIONS
-----------------

This flaw exists in the following curl versions.

- Affected versions: curl 7.1 to and including 7.50.3
- Not affected versions: curl >= 7.51.0

libcurl is used by many applications, but not always advertised as such!

_Trimmed to 38 lines — full report: https://hackerone.com/reports/180434_
