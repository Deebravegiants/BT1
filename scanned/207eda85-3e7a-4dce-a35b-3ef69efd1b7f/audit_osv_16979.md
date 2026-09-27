# [M] CVE-2020-11019

## Summary
Severity: Medium
Advisory: CVE-2020-11019
Aliases: GHSA-wvrr-2f4r-hjvh
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-29
Source: https://osv.dev/vulnerability/CVE-2020-11019
Type: osv

## Details
In FreeRDP less than or equal to 2.0.0, when running with logger set to "WLOG_TRACE", a possible crash of application could occur due to a read of an invalid array index. Data could be printed as string to local terminal. This has been fixed in 2.1.0.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-wvrr-2f4r-hjvh
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
