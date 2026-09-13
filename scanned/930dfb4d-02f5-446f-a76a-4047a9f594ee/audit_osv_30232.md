# [M] posix-clock: posix-clock: Fix unbalanced locking in pc_clock_settime()

## Summary
Severity: Medium
Advisory: CVE-2024-50210
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50210
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.228 <5.10.229, >=5.15.169 <5.15.170, >=6.1.114 <6.1.115, >=6.6.58 <6.6.59, >=6.11.5 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

posix-clock: posix-clock: Fix unbalanced locking in pc_clock_settime()

If get_clock_desc() succeeds, it calls fget() for the clockid's fd,
and get the clk->rwsem read lock, so the error path should release
the lock to make the lock balance and fput the clockid's fd to make
the refcount balance and release the fd related resource.

However the below commit left the error path locked behind resulting in
unbalanced locking. Check timespec64_valid_strict() before
get_clock_desc() to fix it, because the "ts" is not changed
after that.

[pabeni@redhat.com: fixed commit message typo]

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/1ba33b327c3f88a7baee598979d73ab5b44d41cc
- https://git.kernel.org/stable/c/5f063bbf1ee6b01611c016b54e050a41506eb794
- https://git.kernel.org/stable/c/6e62807c7fbb3c758d233018caf94dfea9c65dbd
- https://git.kernel.org/stable/c/a8219446b95a859488feaade674d13f9efacfa32
- https://git.kernel.org/stable/c/b27330128eca25179637c1816d5a72d6cc408c66
- https://git.kernel.org/stable/c/c7fcfdba35abc9f39b83080c2bce398dad13a943
- https://git.kernel.org/stable/c/d005400262ddaf1ca1666bbcd1acf42fe81d57ce
- https://git.kernel.org/stable/c/e56e0ec1b79f5a6272c6e78b36e9d593aa0449af
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50210.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50210
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
