# [H] ALPINE-CVE-2023-50269

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-50269
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-50269
Type: osv

## Affected
- Alpine:v3.19: `squid` — affected >=3.1 <6.6-r0
- Alpine:v3.20: `squid` — affected >=3.1 <6.6-r0
- Alpine:v3.21: `squid` — affected >=3.1 <6.6-r0
- Alpine:v3.22: `squid` — affected >=3.1 <6.6-r0
- Alpine:v3.23: `squid` — affected >=3.1 <6.6-r0
- Alpine:v3.24: `squid` — affected >=3.1 <6.6-r0

## Details
Squid is a caching proxy for the Web. Due to an Uncontrolled Recursion bug in versions 2.6 through 2.7.STABLE9, versions 3.1 through 5.9, and versions 6.0.1 through 6.5, Squid may be vulnerable to a Denial of Service attack against HTTP Request parsing. This problem allows a remote client to perform Denial of Service attack by sending a large X-Forwarded-For header when the follow_x_forwarded_for feature is configured. This bug is fixed by Squid version 6.6. In addition, patches addressing this problem for the stable releases can be found in Squid's patch archives.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-50269
