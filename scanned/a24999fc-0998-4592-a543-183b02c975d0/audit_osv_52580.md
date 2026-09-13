# [M] CVE-2021-47602

## Summary
Severity: Medium
Advisory: CVE-2021-47602
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47602
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mac80211: track only QoS data frames for admission control

For admission control, obviously all of that only works for
QoS data frames, otherwise we cannot even access the QoS
field in the header.

Syzbot reported (see below) an uninitialized value here due
to a status of a non-QoS nullfunc packet, which isn't even
long enough to contain the QoS header.

Fix this to only do anything for QoS data packets.

## References
- https://git.kernel.org/stable/c/d5e568c3a4ec2ddd23e7dc5ad5b0c64e4f22981a
- https://git.kernel.org/stable/c/eed897a22230e3231a740eddd7d6d95ba476625f
- https://git.kernel.org/stable/c/42d08e97b196479f593499e887a9ab81446a34b9
- https://git.kernel.org/stable/c/46b9e29db2012a4d2a40a26101862e002ccf387b
- https://git.kernel.org/stable/c/69f054d6642c8f6173724ce17e7ee3ff66b8f682
