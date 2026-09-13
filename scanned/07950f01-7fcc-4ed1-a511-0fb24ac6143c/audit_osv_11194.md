# [C] CVE-2017-6519

## Summary
Severity: Critical
Advisory: CVE-2017-6519
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2017-6519
Type: osv

## Details
avahi-daemon in Avahi through 0.6.32 and 0.7 inadvertently responds to IPv6 unicast queries with source addresses that are not on-link, which allows remote attackers to cause a denial of service (traffic amplification) and may cause information leakage by obtaining potentially sensitive  information from the responding device via port-5353 UDP packets.  NOTE: this may overlap CVE-2015-2809.

## References
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0%40%3Cissues.bookkeeper.apache.org%3E
- https://github.com/lathiat/avahi/issues/203#issuecomment-449536790
- https://usn.ubuntu.com/3876-1/
- https://usn.ubuntu.com/3876-2/
- https://www.secfu.net/advisories
- https://bugzilla.redhat.com/show_bug.cgi?id=1426712
- https://github.com/lathiat/avahi/issues/203
