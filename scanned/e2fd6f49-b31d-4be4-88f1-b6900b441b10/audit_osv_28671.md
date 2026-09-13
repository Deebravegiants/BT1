# [H] x86/coco: Require seeding RNG with RDRAND on CoCo systems

## Summary
Severity: High
Advisory: CVE-2024-35875
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35875
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/coco: Require seeding RNG with RDRAND on CoCo systems

There are few uses of CoCo that don't rely on working cryptography and
hence a working RNG. Unfortunately, the CoCo threat model means that the
VM host cannot be trusted and may actively work against guests to
extract secrets or manipulate computation. Since a malicious host can
modify or observe nearly all inputs to guests, the only remaining source
of entropy for CoCo guests is RDRAND.

If RDRAND is broken -- due to CPU hardware fault -- the RNG as a whole
is meant to gracefully continue on gathering entropy from other sources,
but since there aren't other sources on CoCo, this is catastrophic.
This is mostly a concern at boot time when initially seeding the RNG, as
after that the consequences of a broken RDRAND are much more
theoretical.

So, try at boot to seed the RNG using 256 bits of RDRAND output. If this
fails, panic(). This will also trigger if the system is booted without
RDRAND, as RDRAND is essential for a safe CoCo boot.

Add this deliberately to be "just a CoCo x86 driver feature" and not
part of the RNG itself. Many device drivers and platforms have some
desire to contribute something to the RNG, and add_device_randomness()
is specifically meant for this purpose.

Any driver can call it with seed data of any quality, or even garbage
quality, and it can only possibly make the quality of the RNG better or
have no effect, but can never make it worse.

Rather than trying to build something into the core of the RNG, consider
the particular CoCo issue just a CoCo issue, and therefore separate it
all out into driver (well, arch/platform) code.

  [ bp: Massage commit message. ]

## References
- https://git.kernel.org/stable/c/08044b08b37528b82f70a87576c692b4e4b7716e
- https://git.kernel.org/stable/c/22943e4fe4b3a2dcbadc3d38d5bf840bbdbfe374
- https://git.kernel.org/stable/c/453b5f2dec276c1bb4ea078bf8c0da57ee4627e5
- https://git.kernel.org/stable/c/99485c4c026f024e7cb82da84c7951dbe3deb584
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35875.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35875
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
