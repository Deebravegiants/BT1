# [H] ALSA: hda/cs_dsp_ctl: Use private_free for control cleanup

## Summary
Severity: High
Advisory: CVE-2024-38388
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2024-38388
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: hda/cs_dsp_ctl: Use private_free for control cleanup

Use the control private_free callback to free the associated data
block. This ensures that the memory won't leak, whatever way the
control gets destroyed.

The original implementation didn't actually remove the ALSA
controls in hda_cs_dsp_control_remove(). It only freed the internal
tracking structure. This meant it was possible to remove/unload the
amp driver while leaving its ALSA controls still present in the
soundcard. Obviously attempting to access them could cause segfaults
or at least dereferencing stale pointers.

## References
- https://git.kernel.org/stable/c/172811e3a557d8681a5e2d0f871dc04a2d17eb13
- https://git.kernel.org/stable/c/191dc1b2ff0fb35e7aff15a53224837637df8bff
- https://git.kernel.org/stable/c/3291486af5636540980ea55bae985f3eaa5b0740
- https://git.kernel.org/stable/c/6e359be4975006ff72818e79dad8fe48293f2eb2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38388.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38388
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
