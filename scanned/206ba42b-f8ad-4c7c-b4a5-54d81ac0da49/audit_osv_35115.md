# [H] ALSA: firewire-motu: fix buffer overflow in hwdep read for DSP events

## Summary
Severity: High
Advisory: CVE-2025-68347
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68347
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.63, >=6.13.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: firewire-motu: fix buffer overflow in hwdep read for DSP events

The DSP event handling code in hwdep_read() could write more bytes to
the user buffer than requested, when a user provides a buffer smaller
than the event header size (8 bytes).

Fix by using min_t() to clamp the copy size, This ensures we never copy
more than the user requested.

## References
- https://git.kernel.org/stable/c/161291bac551821bba98eb4ea84c82338578d1b0
- https://git.kernel.org/stable/c/16620f0617400746984362c3d6ac547eeae1d35f
- https://git.kernel.org/stable/c/210d77cca3d0494ed30a5c628b20c1d95fa04fb1
- https://git.kernel.org/stable/c/6275fd726d53a8ec724f20201cf3bd862711e17b
- https://git.kernel.org/stable/c/cdda0d06f8650e33255f79839f188bbece44117c
- https://git.kernel.org/stable/c/ddd32ec66bc4eb6969fe835e4cc1c0706c6348fe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68347.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68347
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
