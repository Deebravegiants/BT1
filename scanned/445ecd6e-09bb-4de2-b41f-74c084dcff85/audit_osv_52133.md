# [M] CVE-2021-47109

## Summary
Severity: Medium
Advisory: CVE-2021-47109
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2021-47109
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

neighbour: allow NUD_NOARP entries to be forced GCed

IFF_POINTOPOINT interfaces use NUD_NOARP entries for IPv6. It's possible to
fill up the neighbour table with enough entries that it will overflow for
valid connections after that.

This behaviour is more prevalent after commit 58956317c8de ("neighbor:
Improve garbage collection") is applied, as it prevents removal from
entries that are not NUD_FAILED, unless they are more than 5s old.

## References
- https://git.kernel.org/stable/c/d17d47da59f726dc4c87caebda3a50333d7e2fd3
- https://git.kernel.org/stable/c/d99029e6aab62aef0a0251588b2867e77e83b137
- https://git.kernel.org/stable/c/ddf088d7aaaaacfc836104f2e632b29b1d383cfc
- https://git.kernel.org/stable/c/7a6b1ab7475fd6478eeaf5c9d1163e7a18125c8f
