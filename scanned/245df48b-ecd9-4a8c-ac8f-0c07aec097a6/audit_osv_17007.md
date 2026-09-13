# [M] CVE-2020-11086

## Summary
Severity: Medium
Advisory: CVE-2020-11086
Aliases: GHSA-fg8v-w34r-c974
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2020-05-29
Source: https://osv.dev/vulnerability/CVE-2020-11086
Type: osv

## Details
In FreeRDP less than or equal to 2.0.0, there is an out-of-bound read in ntlm_read_ntlm_v2_client_challenge that reads up to 28 bytes out-of-bound to an internal structure. This has been fixed in 2.1.0.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://github.com/FreeRDP/FreeRDP/commit/c098f21fdaadca57ff649eee1674f6cc321a2ec4
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-fg8v-w34r-c974
