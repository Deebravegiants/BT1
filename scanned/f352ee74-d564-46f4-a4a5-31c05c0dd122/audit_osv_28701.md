# [H] wifi: cfg80211: check A-MSDU format more carefully

## Summary
Severity: High
Advisory: CVE-2024-35937
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35937
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.27, >=6.7.0 <6.8.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: check A-MSDU format more carefully

If it looks like there's another subframe in the A-MSDU
but the header isn't fully there, we can end up reading
data out of bounds, only to discard later. Make this a
bit more careful and check if the subframe header can
even be present.

## References
- https://git.kernel.org/stable/c/16da1e1dac23be45ef6e23c41b1508c400e6c544
- https://git.kernel.org/stable/c/5d7a8585fbb31e88fb2a0f581b70667d3300d1e9
- https://git.kernel.org/stable/c/9ad7974856926129f190ffbe3beea78460b3b7cc
- https://git.kernel.org/stable/c/9eb3bc0973d084423a6df21cf2c74692ff05647e
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35937.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35937
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
