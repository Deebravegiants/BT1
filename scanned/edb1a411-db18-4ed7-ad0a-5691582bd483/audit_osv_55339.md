# [H] CVE-2025-32318

## Summary
Severity: High
Advisory: CVE-2025-32318
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-32318
Type: osv

## Details
In Skia, there is a possible out of bounds write due to a heap buffer overflow. This could lead to remote escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.

## References
- https://source.android.com/security/bulletin/android-16
