# [H] CVE-2017-7506

## Summary
Severity: High
Advisory: CVE-2017-7506
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-18
Source: https://osv.dev/vulnerability/CVE-2017-7506
Type: osv

## Details
spice versions though 0.13 are vulnerable to out-of-bounds memory access when processing specially crafted messages from authenticated attacker to the spice server resulting into crash and/or server memory leak.

## References
- http://www.debian.org/security/2017/dsa-3907
- http://www.openwall.com/lists/oss-security/2017/07/14/1
- http://www.securityfocus.com/bid/99583
- https://access.redhat.com/errata/RHSA-2017:2471
- https://access.redhat.com/errata/RHSA-2018:3522
- https://bugzilla.redhat.com/show_bug.cgi?id=1452606
