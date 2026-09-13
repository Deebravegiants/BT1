# [H] CVE-2017-0553

## Summary
Severity: High
Advisory: CVE-2017-0553
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-07
Source: https://osv.dev/vulnerability/CVE-2017-0553
Type: osv

## Details
An elevation of privilege vulnerability in libnl could enable a local malicious application to execute arbitrary code within the context of the Wi-Fi service. This issue is rated as Moderate because it first requires compromising a privileged process and is mitigated by current platform configurations. Product: Android. Versions: 5.0.2, 5.1.1, 6.0, 6.0.1, 7.0, 7.1.1. Android ID: A-32342065. NOTE: this issue also exists in the upstream libnl before 3.3.0 library.

## References
- http://lists.infradead.org/pipermail/libnl/2017-May/002313.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6VCF5KS6HOJZLFIY2ZSXSVSDQX65A2PU/
- http://git.infradead.org/users/tgr/libnl.git/commit/3e18948f17148e6a3c4255bdeaaf01ef6081ceeb
- http://www.securitytracker.com/id/1038201
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KIHASXRQO2YTQPKVP4VGIB2XHPANG6YX/
- http://www.securityfocus.com/bid/97340
- http://www.ubuntu.com/usn/USN-3311-2
- https://source.android.com/security/bulletin/2017-04-01
- https://access.redhat.com/errata/RHSA-2017:2299
- https://usn.ubuntu.com/usn/usn-3311-1/
