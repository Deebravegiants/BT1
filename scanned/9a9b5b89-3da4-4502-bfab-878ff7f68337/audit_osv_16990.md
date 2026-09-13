# [M] CVE-2020-11042

## Summary
Severity: Medium
Advisory: CVE-2020-11042
Aliases: GHSA-9jp6-5vf2-cx2q
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-05-07
Source: https://osv.dev/vulnerability/CVE-2020-11042
Type: osv

## Details
In FreeRDP greater than 1.1 and before 2.0.0, there is an out-of-bounds read in update_read_icon_info. It allows reading a attacker-defined amount of client memory (32bit unsigned -> 4GB) to an intermediate buffer. This can be used to crash the client or store information for later retrieval. This has been patched in 2.0.0.

## References
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-9jp6-5vf2-cx2q
- https://lists.debian.org/debian-lts-announce/2020/08/msg00054.html
- https://usn.ubuntu.com/4379-1/
- https://usn.ubuntu.com/4382-1/
- https://github.com/FreeRDP/FreeRDP/commit/6b2bc41935e53b0034fe5948aeeab4f32e80f30f
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
- https://github.com/FreeRDP/FreeRDP/issues/6010
