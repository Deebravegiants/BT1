# [H] CVE-2020-0110

## Summary
Severity: High
Advisory: CVE-2020-0110
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-14
Source: https://osv.dev/vulnerability/CVE-2020-0110
Type: osv

## Details
In psi_write of psi.c, there is a possible out of bounds write due to a missing bounds check. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-148159562References: Upstream kernel

## References
- https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00533.html
- https://source.android.com/security/bulletin/2020-05-01
