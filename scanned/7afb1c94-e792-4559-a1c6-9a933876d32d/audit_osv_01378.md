# [M] ALPINE-CVE-2019-12529

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-12529
Ecosystem: Alpine:v3.10, Alpine:v3.9
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12529
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=2.0 <4.8-r0
- Alpine:v3.9: `squid` — affected >=2.0 <4.8-r0

## Details
An issue was discovered in Squid 2.x through 2.7.STABLE9, 3.x through 3.5.28, and 4.x through 4.7. When Squid is configured to use Basic Authentication, the Proxy-Authorization header is parsed via uudecode. uudecode determines how many bytes will be decoded by iterating over the input and checking its table. The length is then used to start decoding the string. There are no checks to ensure that the length it calculates isn't greater than the input buffer. This leads to adjacent memory being decoded as well. An attacker would not be able to retrieve the decoded data unless the Squid maintainer had configured the display of usernames on error pages.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12529
