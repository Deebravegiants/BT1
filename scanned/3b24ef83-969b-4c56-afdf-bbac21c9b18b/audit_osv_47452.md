# [H] CVE-2016-5285

## Summary
Severity: High
Advisory: CVE-2016-5285
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-15
Source: https://osv.dev/vulnerability/CVE-2016-5285
Type: osv

## Details
A Null pointer dereference vulnerability exists in Mozilla Network Security Services due to a missing NULL check in PK11_SignWithSymKey / ssl3_ComputeRecordMACConstantTime, which could let a remote malicious user cause a Denial of Service.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00037.html
- http://www.securityfocus.com/bid/94349
- https://bto.bluecoat.com/security-advisory/sa137
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00049.html
- http://rhn.redhat.com/errata/RHSA-2016-2779.html
- http://www.ubuntu.com/usn/USN-3163-1
- https://security.gentoo.org/glsa/201701-46
- https://bugzilla.mozilla.org/show_bug.cgi?id=1306103
