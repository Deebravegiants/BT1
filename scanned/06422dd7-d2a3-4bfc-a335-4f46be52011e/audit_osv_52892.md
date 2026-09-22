# [M] CVE-2022-20423

## Summary
Severity: Medium
Advisory: CVE-2022-20423
Aliases: A-239842288, ASB-A-239842288
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/CVE-2022-20423
Type: osv

## Details
In rndis_set_response of rndis.c, there is a possible out of bounds write due to an integer overflow. This could lead to local escalation of privilege if a malicious USB device is attached with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-239842288References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2022-10-01
- https://source.android.com/security/bulletin/2022-10-01
