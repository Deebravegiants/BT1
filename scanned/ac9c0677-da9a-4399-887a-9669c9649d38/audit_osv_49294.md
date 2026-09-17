# [H] CVE-2018-9518

## Summary
Severity: High
Advisory: CVE-2018-9518
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-9518
Type: osv

## Details
In nfc_llcp_build_sdreq_tlv of llcp_commands.c, there is a possible out of bounds write due to a missing bounds check. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation. Product: Android. Versions: Android kernel. Android ID: A-73083945.

## References
- https://source.android.com/security/bulletin/pixel/2018-09-01
- https://usn.ubuntu.com/3798-2/
- https://usn.ubuntu.com/3798-1/
