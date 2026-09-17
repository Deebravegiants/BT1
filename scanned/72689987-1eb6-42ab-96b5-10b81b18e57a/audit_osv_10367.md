# [H] CVE-2017-15124

## Summary
Severity: High
Advisory: CVE-2017-15124
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-09
Source: https://osv.dev/vulnerability/CVE-2017-15124
Type: osv

## Details
VNC server implementation in Quick Emulator (QEMU) 2.11.0 and older was found to be vulnerable to an unbounded memory allocation issue, as it did not throttle the framebuffer updates sent to its client. If the client did not consume these updates, VNC server allocates growing memory to hold onto this data. A malicious remote VNC client could use this flaw to cause DoS to the server host.

## References
- http://www.securityfocus.com/bid/102295
- https://usn.ubuntu.com/3575-1/
- https://access.redhat.com/errata/RHSA-2018:0816
- https://access.redhat.com/errata/RHSA-2018:1104
- https://access.redhat.com/errata/RHSA-2018:1113
- https://access.redhat.com/errata/RHSA-2018:3062
- https://www.debian.org/security/2018/dsa-4213
- https://bugzilla.redhat.com/show_bug.cgi?id=1525195
