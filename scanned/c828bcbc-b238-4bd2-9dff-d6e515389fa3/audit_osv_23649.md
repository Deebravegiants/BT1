# [H] mac80211: fix potential double free on mesh join

## Summary
Severity: High
Advisory: CVE-2022-49290
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49290
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.9.309, >=4.10.0 <4.14.274, >=4.15.0 <4.19.237, >=4.20.0 <5.4.188, >=5.5.0 <5.10.109, >=5.8.0 <5.15.32, >=5.11.0 <5.16.18, >=5.16.0 <5.17.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

mac80211: fix potential double free on mesh join

While commit 6a01afcf8468 ("mac80211: mesh: Free ie data when leaving
mesh") fixed a memory leak on mesh leave / teardown it introduced a
potential memory corruption caused by a double free when rejoining the
mesh:

  ieee80211_leave_mesh()
  -> kfree(sdata->u.mesh.ie);
  ...
  ieee80211_join_mesh()
  -> copy_mesh_setup()
     -> old_ie = ifmsh->ie;
     -> kfree(old_ie);

This double free / kernel panics can be reproduced by using wpa_supplicant
with an encrypted mesh (if set up without encryption via "iw" then
ifmsh->ie is always NULL, which avoids this issue). And then calling:

  $ iw dev mesh0 mesh leave
  $ iw dev mesh0 mesh join my-mesh

Note that typically these commands are not used / working when using
wpa_supplicant. And it seems that wpa_supplicant or wpa_cli are going
through a NETDEV_DOWN/NETDEV_UP cycle between a mesh leave and mesh join
where the NETDEV_UP resets the mesh.ie to NULL via a memcpy of
default_mesh_setup in cfg80211_netdev_notifier_call, which then avoids
the memory corruption, too.

The issue was first observed in an application which was not using
wpa_supplicant but "Senf" instead, which implements its own calls to
nl80211.

Fixing the issue by removing the kfree()'ing of the mesh IE in the mesh
join function and leaving it solely up to the mesh leave to free the
mesh IE.

## References
- https://git.kernel.org/stable/c/12e407a8ef17623823fd0c066fbd7f103953d28d
- https://git.kernel.org/stable/c/273ebddc5fda2967492cb0b6cdd7d81cfb821b76
- https://git.kernel.org/stable/c/3bbd0000d012f92aec423b224784fbf0f7bf40f8
- https://git.kernel.org/stable/c/46bb87d40683337757a2f902fcd4244b32bb4e86
- https://git.kernel.org/stable/c/4a2d4496e15ea5bb5c8e83b94ca8ca7fb045e7d3
- https://git.kernel.org/stable/c/582d8c60c0c053684f7138875e8150d5749ffc17
- https://git.kernel.org/stable/c/5d3ff9542a40ce034416bca03864709540a36016
- https://git.kernel.org/stable/c/615716af8644813355e014314a0bc1e961250f5a
- https://git.kernel.org/stable/c/c1d9c3628ef0a0ca197595d0f9e01cd3b5dda186
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49290.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49290
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
