# [H] CVE-2022-20566

## Summary
Severity: High
Advisory: CVE-2022-20566
Aliases: A-165329981, PUB-A-165329981
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-16
Source: https://osv.dev/vulnerability/CVE-2022-20566
Type: osv

## Details
In l2cap_chan_put of l2cap_core, there is a possible use after free due to improper locking. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-165329981References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2022-12-01
- https://source.android.com/security/bulletin/pixel/2022-12-01
