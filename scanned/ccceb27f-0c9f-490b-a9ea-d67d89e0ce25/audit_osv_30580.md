# [M] ALSA: pcm: Add sanity NULL check for the default mmap fault handler

## Summary
Severity: Medium
Advisory: CVE-2024-53180
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53180
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: pcm: Add sanity NULL check for the default mmap fault handler

A driver might allow the mmap access before initializing its
runtime->dma_area properly.  Add a proper NULL check before passing to
virt_to_page() for avoiding a panic.

## References
- https://git.kernel.org/stable/c/0c4c9bf5eab7bee6b606f2abb0993e933b5831a0
- https://git.kernel.org/stable/c/832efbb74b1578e3737d593a204d42af8bd1b81b
- https://git.kernel.org/stable/c/8799f4332a9fd812eadfbc32fc5104d6292f754f
- https://git.kernel.org/stable/c/bc200027ee92fba84f1826494735ed675f3aa911
- https://git.kernel.org/stable/c/d2913a07d9037fe7aed4b7e680684163eaed6bc4
- https://git.kernel.org/stable/c/f0ce9e24eff1678c16276f9717f26a78202506a2
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53180.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53180
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
