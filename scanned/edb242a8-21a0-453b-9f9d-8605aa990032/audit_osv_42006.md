# [H] crypto: loongson - Remove broken and unused loongson-rng

## Summary
Severity: High
Advisory: CVE-2026-64311
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64311
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: loongson - Remove broken and unused loongson-rng

The loongson-rng rng_alg has several vulnerabilities, including not
providing forward security, and a use-after-free bug due to the use of
wait_for_completion_interruptible().

Meanwhile, the rng_alg framework doesn't really have any purpose in the
first place other than to access the software algorithms crypto/drbg.c
and crypto/jitterentropy.c.  Hardware-specific rng_algs have no
in-kernel user, and unlike hwrng there's no feed into the actual Linux
RNG.  As such, there's really no point to this code.  There are of
course other rng_alg drivers that are similarly unused, but they're
similarly in the process of being phased out, e.g.
https://lore.kernel.org/r/20260529193648.18172-1-ebiggers@kernel.org and
https://lore.kernel.org/r/20260529220430.34135-1-ebiggers@kernel.org

Given that, there's no point in fixing forward these vulnerabilities,
and it makes much more sense to simply roll back the addition of this
driver.  If this platform provides TRNG (not PRNG) functionality, it
could make sense to add a hwrng driver, but it would be quite different.

## References
- https://git.kernel.org/stable/c/037ec8353711c79353b12d5634e0c9ff363a9efa
- https://git.kernel.org/stable/c/43de8b9f01b7dd2f6ca5360c6bf2f203c02288dc
- https://git.kernel.org/stable/c/af3d1bb9a09daf928fc3f173689fb7904d6a6d4f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64311.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64311
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
