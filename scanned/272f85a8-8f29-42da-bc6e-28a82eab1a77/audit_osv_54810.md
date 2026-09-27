# [C] CVE-2024-45237

## Summary
Severity: Critical
Advisory: CVE-2024-45237
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-24
Source: https://osv.dev/vulnerability/CVE-2024-45237
Type: osv

## Details
An issue was discovered in Fort before 1.6.3. A malicious RPKI repository that descends from a (trusted) Trust Anchor can serve (via rsync or RRDP) a resource certificate containing a Key Usage extension composed of more than two bytes of data. Fort writes this string into a 2-byte buffer without properly sanitizing its length, leading to a buffer overflow.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00030.html
- https://nicmx.github.io/FORT-validator/CVE.html
