# [H] CVE-2016-5361

## Summary
Severity: High
Advisory: CVE-2016-5361
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-16
Source: https://osv.dev/vulnerability/CVE-2016-5361
Type: osv

## Details
programs/pluto/ikev1.c in libreswan before 3.17 retransmits in initial-responder states, which allows remote attackers to cause a denial of service (traffic amplification) via a spoofed UDP packet. NOTE: the original behavior complies with the IKEv1 protocol, but has a required security update from the libreswan vendor; as of 2016-06-10, it is expected that several other IKEv1 implementations will have vendor-required security updates, with separate CVE IDs assigned to each.

## References
- http://www.openwall.com/lists/oss-security/2016/06/10/4
- https://lists.libreswan.org/pipermail/swan-dev/2016-March/001394.html
- http://rhn.redhat.com/errata/RHSA-2016-2603.html
- https://github.com/libreswan/libreswan/commit/152d6d95632d8b9477c170f1de99bcd86d7fb1d6
