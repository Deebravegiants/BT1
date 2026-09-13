# [M] CVE-2020-11018

## Summary
Severity: Medium
Advisory: CVE-2020-11018
Aliases: GHSA-8cvc-vcw7-6mfw
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-29
Source: https://osv.dev/vulnerability/CVE-2020-11018
Type: osv

## Details
In FreeRDP less than or equal to 2.0.0, a possible resource exhaustion vulnerability can be performed. Malicious clients could trigger out of bound reads causing memory allocation with random size. This has been fixed in 2.1.0.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-8cvc-vcw7-6mfw
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
