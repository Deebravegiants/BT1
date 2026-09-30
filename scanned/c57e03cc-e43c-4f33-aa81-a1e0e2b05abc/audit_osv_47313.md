# [H] CVE-2016-2464

## Summary
Severity: High
Advisory: CVE-2016-2464
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-06-13
Source: https://osv.dev/vulnerability/CVE-2016-2464
Type: osv

## Details
libvpx in libwebm in mediaserver in Android 4.x before 4.4.4, 5.0.x before 5.0.2, 5.1.x before 5.1.1, and 6.x before 2016-06-01 allows remote attackers to execute arbitrary code or cause a denial of service (memory corruption) via a crafted mkv file, aka internal bug 23167726.

## References
- https://android.googlesource.com/platform/external/libvpx/+/65c49d5b382de4085ee5668732bcb0f6ecaf7148
- https://android.googlesource.com/platform/external/libvpx/+/cc274e2abe8b2a6698a5c47d8aa4bb45f1f9538d
- http://source.android.com/security/bulletin/2016-06-01.html
