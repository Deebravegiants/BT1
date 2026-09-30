# [M] staging: greybus: audio_helper: remove unused and wrong debugfs usage

## Summary
Severity: Medium
Advisory: CVE-2022-50400
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50400
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: greybus: audio_helper: remove unused and wrong debugfs usage

In the greybus audio_helper code, the debugfs file for the dapm has the
potential to be removed and memory will be leaked.  There is also the
very real potential for this code to remove ALL debugfs entries from the
system, and it seems like this is what will really happen if this code
ever runs.  This all is very wrong as the greybus audio driver did not
create this debugfs file, the sound core did and controls the lifespan
of it.

So remove all of the debugfs logic from the audio_helper code as there's
no way it could be correct.  If this really is needed, it can come back
with a fixup for the incorrect usage of the debugfs_lookup() call which
is what caused this to be noticed at all.

## References
- https://git.kernel.org/stable/c/4dab0d27a4211a27135a6899d6c737e6e0759a11
- https://git.kernel.org/stable/c/5699afbff1fa2972722e863906c0320d55dd4d58
- https://git.kernel.org/stable/c/d0febad83e29d85bb66e4f5cac0115b022403338
- https://git.kernel.org/stable/c/d517cdeb904ddc0cbebcc959d43596426cac40b0
- https://git.kernel.org/stable/c/d835fa49d9589a780ff0d001bb7e6323238a4afb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50400.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50400
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
