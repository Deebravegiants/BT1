# [H] CVE-2017-11499

## Summary
Severity: High
Advisory: CVE-2017-11499
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-25
Source: https://osv.dev/vulnerability/CVE-2017-11499
Type: osv

## Details
Node.js v4.0 through v4.8.3, all versions of v5.x, v6.0 through v6.11.0, v7.0 through v7.10.0, and v8.0 through v8.1.3 was susceptible to hash flooding remote DoS attacks as the HashTable seed was constant across a given released version of Node.js. This was a result of building with V8 snapshots enabled by default which caused the initially randomized seed to be overwritten on startup.

## References
- http://www.securityfocus.com/bid/99959
- https://access.redhat.com/errata/RHSA-2017:2908
- https://access.redhat.com/errata/RHSA-2017:3002
- https://nodejs.org/en/blog/vulnerability/july-2017-security-releases/
