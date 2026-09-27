# [H] CVE-2019-2024

## Summary
Severity: High
Advisory: CVE-2019-2024
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-19
Source: https://osv.dev/vulnerability/CVE-2019-2024
Type: osv

## Details
In em28xx_unregister_dvb of em28xx-dvb.c, there is a possible use after free issue. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-111761954References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2019-03-01
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/4118-1/
