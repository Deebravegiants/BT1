# [M] ALSA: hda: fix a possible null-pointer dereference due to data race in snd_hdac_regmap_sync()

## Summary
Severity: Medium
Advisory: CVE-2023-53275
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53275
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.255, >=5.5.0 <5.10.192, >=5.6.0 <5.15.128, >=5.11.0 <6.1.47, >=5.16.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: hda: fix a possible null-pointer dereference due to data race in snd_hdac_regmap_sync()

The variable codec->regmap is often protected by the lock
codec->regmap_lock when is accessed. However, it is accessed without
holding the lock when is accessed in snd_hdac_regmap_sync():

  if (codec->regmap)

In my opinion, this may be a harmful race, because if codec->regmap is
set to NULL right after the condition is checked, a null-pointer
dereference can occur in the called function regcache_sync():

  map->lock(map->lock_arg); --> Line 360 in drivers/base/regmap/regcache.c

To fix this possible null-pointer dereference caused by data race, the
mutex_lock coverage is extended to protect the if statement as well as the
function call to regcache_sync().

[ Note: the lack of the regmap_lock itself is harmless for the current
  codec driver implementations, as snd_hdac_regmap_sync() is only for
  PM runtime resume that is prohibited during the codec probe.
  But the change makes the whole code more consistent, so it's merged
  as is -- tiwai ]

## References
- https://git.kernel.org/stable/c/109f0aaa0b8838a88af9125b79579023539300a7
- https://git.kernel.org/stable/c/1f4a08fed450db87fbb5ff5105354158bdbe1a22
- https://git.kernel.org/stable/c/8703b26387e1fa4f8749db98d24c67617b873acb
- https://git.kernel.org/stable/c/9f9eed451176ffcac6b5ba0f6dae1a6b4a1cb0eb
- https://git.kernel.org/stable/c/b32e40379e5b2814de0c4bc199edc2d82317dc07
- https://git.kernel.org/stable/c/cdd412b528dee6e0851c4735d6676ec138da13a4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53275.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53275
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
