# [H] CVE-2018-9385

## Summary
Severity: High
Advisory: CVE-2018-9385
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-06
Source: https://osv.dev/vulnerability/CVE-2018-9385
Type: osv

## Details
In driver_override_store of bus.c, there is a possible out of bounds write due to an incorrect bounds check. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation. Product: Android Versions: Android kernel Android ID: A-74128061 References: Upstream kernel.

## References
- http://www.securityfocus.com/bid/105887
- https://source.android.com/security/bulletin/pixel/2018-06-01
- https://source.android.com/security/bulletin/pixel/2018-06-01
