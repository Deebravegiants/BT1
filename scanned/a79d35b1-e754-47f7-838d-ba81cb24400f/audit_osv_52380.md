# [H] CVE-2021-47388

## Summary
Severity: High
Advisory: CVE-2021-47388
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47388
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mac80211: fix use-after-free in CCMP/GCMP RX

When PN checking is done in mac80211, for fragmentation we need
to copy the PN to the RX struct so we can later use it to do a
comparison, since commit bf30ca922a0c ("mac80211: check defrag
PN against current frame").

Unfortunately, in that commit I used the 'hdr' variable without
it being necessarily valid, so use-after-free could occur if it
was necessary to reallocate (parts of) the frame.

Fix this by reloading the variable after the code that results
in the reallocations, if any.

This fixes https://bugzilla.kernel.org/show_bug.cgi?id=214401.

## References
- https://git.kernel.org/stable/c/31de381aef0ab1b342f62485118dc8a19363dc78
- https://git.kernel.org/stable/c/3d5d629c99c468458022e9b381789de3595bf4dd
- https://git.kernel.org/stable/c/447d001b875d0e7f211c4ba004916028da994258
- https://git.kernel.org/stable/c/50149e0866a82cef33e680ee68dc380a5bc75d32
- https://git.kernel.org/stable/c/57de2dcb18742dc2860861c9f496da7d42b67da0
- https://git.kernel.org/stable/c/94513069eb549737bcfc3d988d6ed4da948a2de8
- https://git.kernel.org/stable/c/f556e1d6fb9f2923a9a36f3df638c7d79ba09dbb
- https://git.kernel.org/stable/c/27d3eb5616ee2c0a3b30c3fa34813368ed1f3dc9
