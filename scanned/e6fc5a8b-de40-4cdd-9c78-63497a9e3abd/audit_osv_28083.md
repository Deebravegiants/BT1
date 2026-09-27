# [H] wifi: nl80211: reject iftype change with mesh ID change

## Summary
Severity: High
Advisory: CVE-2024-27410
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-27410
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.81, >=6.2.0 <6.6.21, >=6.7.0 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: nl80211: reject iftype change with mesh ID change

It's currently possible to change the mesh ID when the
interface isn't yet in mesh mode, at the same time as
changing it into mesh mode. This leads to an overwrite
of data in the wdev->u union for the interface type it
currently has, causing cfg80211_change_iface() to do
wrong things when switching.

We could probably allow setting an interface to mesh
while setting the mesh ID at the same time by doing a
different order of operations here, but realistically
there's no userspace that's going to do this, so just
disallow changes in iftype when setting mesh ID.

## References
- https://git.kernel.org/stable/c/063715c33b4c37587aeca2c83cf08ead0c542995
- https://git.kernel.org/stable/c/0cfbb26ee5e7b3d6483a73883f9f6157bca22ec9
- https://git.kernel.org/stable/c/177d574be4b58f832354ab1ef5a297aa0c9aa2df
- https://git.kernel.org/stable/c/930e826962d9f01dcd2220176134427358d112f2
- https://git.kernel.org/stable/c/99eb2159680af8786104dac80528acd5acd45980
- https://git.kernel.org/stable/c/a2add961a5ed25cfd6a74f9ffb9e7ab6d6ded838
- https://git.kernel.org/stable/c/d38d31bbbb9dc0d4d71a45431eafba03d0bc150d
- https://git.kernel.org/stable/c/f78c1375339a291cba492a70eaf12ec501d28a8e
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27410.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27410
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
