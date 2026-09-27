# [H] gpiolib: cdev: fix uninitialised kfifo

## Summary
Severity: High
Advisory: CVE-2024-36898
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36898
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.15.203, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpiolib: cdev: fix uninitialised kfifo

If a line is requested with debounce, and that results in debouncing
in software, and the line is subsequently reconfigured to enable edge
detection then the allocation of the kfifo to contain edge events is
overlooked.  This results in events being written to and read from an
uninitialised kfifo.  Read events are returned to userspace.

Initialise the kfifo in the case where the software debounce is
already active.

## References
- https://git.kernel.org/stable/c/1a51e24404d77bb3307c1e39eee0d8e86febb1a5
- https://git.kernel.org/stable/c/883e4bbf06eb5fb7482679e4edb201093e9f55a2
- https://git.kernel.org/stable/c/bd7139a70ee8d8ea872b223e043730cf6f5e2b0e
- https://git.kernel.org/stable/c/c87cc32bc48b187067e089b15ab7a6a7eed5767d
- https://git.kernel.org/stable/c/ee0166b637a5e376118e9659e5b4148080f1d27e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36898.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36898
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
