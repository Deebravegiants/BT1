# [M] CVE-2020-11039

## Summary
Severity: Medium
Advisory: CVE-2020-11039
Aliases: GHSA-mx9p-f6q8-mqwq
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:L)
Published: 2020-05-29
Source: https://osv.dev/vulnerability/CVE-2020-11039
Type: osv

## Details
In FreeRDP less than or equal to 2.0.0, when using a manipulated server with USB redirection enabled (nearly) arbitrary memory can be read and written due to integer overflows in length checks. This has been patched in 2.1.0.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-mx9p-f6q8-mqwq
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
