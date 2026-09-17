# [H] platform/x86: panasonic-laptop: Fix SINF array out of bounds accesses

## Summary
Severity: High
Advisory: CVE-2024-46859
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46859
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <5.15.168, >=5.16.0 <6.1.111, >=6.2.0 <6.6.52, >=6.7.0 <6.10.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: panasonic-laptop: Fix SINF array out of bounds accesses

The panasonic laptop code in various places uses the SINF array with index
values of 0 - SINF_CUR_BRIGHT(0x0d) without checking that the SINF array
is big enough.

Not all panasonic laptops have this many SINF array entries, for example
the Toughbook CF-18 model only has 10 SINF array entries. So it only
supports the AC+DC brightness entries and mute.

Check that the SINF array has a minimum size which covers all AC+DC
brightness entries and refuse to load if the SINF array is smaller.

For higher SINF indexes hide the sysfs attributes when the SINF array
does not contain an entry for that attribute, avoiding show()/store()
accessing the array out of bounds and add bounds checking to the probe()
and resume() code accessing these.

## References
- https://git.kernel.org/stable/c/6821a82616f60aa72c5909b3e252ad97fb9f7e2a
- https://git.kernel.org/stable/c/9291fadbd2720a869b1d2fcf82305648e2e62a16
- https://git.kernel.org/stable/c/b38c19783286a71693c2194ed1b36665168c09c4
- https://git.kernel.org/stable/c/b7c2f692307fe704be87ea80d7328782b33c3cef
- https://git.kernel.org/stable/c/f52e98d16e9bd7dd2b3aef8e38db5cbc9899d6a4
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46859.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46859
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
