# [H] ALPINE-CVE-2017-9347

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9347
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9347
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.2.0 <2.2.7-r0

## Details
In Wireshark 2.2.0 to 2.2.6, the ROS dissector could crash with a NULL pointer dereference. This was addressed in epan/dissectors/asn1/ros/packet-ros-template.c by validating an OID.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9347
