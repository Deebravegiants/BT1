# [H] crypto: sun4i-ss - Remove insecure and unused rng_alg

## Summary
Severity: High
Advisory: CVE-2026-74438
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74438
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: sun4i-ss - Remove insecure and unused rng_alg

Remove sun4i_ss_rng, as it is insecure and unused:

- It has multiple vulnerabilities.  sun4i_ss_prng_seed() is missing
  locking and has a buffer overflow.  sun4i_ss_prng_generate() fails to
  fill the entire buffer with cryptographic random bytes, because it
  rounds the destination length down and also doesn't actually wait for
  the hardware to be ready before pulling bytes from it.

- No user of this code is known.  It's usable only theoretically via the
  "rng" algorithm type of AF_ALG.  But userspace actually just uses the
  actual Linux RNG (/dev/random etc) instead.  And rng_algs don't
  contribute entropy to the actual Linux RNG either.  (This may have
  been confused with hwrng, which does contribute entropy.)

The sun4i_ss_prng_seed() buffer overflow was reported by Tianchu Chen
and discovered by Atuin - Automated Vulnerability Discovery Engine

There's no point in fixing all these vulnerabilities individually when
this is unused code, so let's just remove it.

## References
- https://git.kernel.org/stable/c/2eafecaba1b46bb9774eaf3556619fd5b6a17c1c
- https://git.kernel.org/stable/c/306ded31bfa00a69d25823a60d7c797170bfb4f8
- https://git.kernel.org/stable/c/9c8086d9511189c34dfa3f9e3a03f2bee12f56a5
- https://git.kernel.org/stable/c/b2c41fa9dd8fc740c489e060b199165771f268d1
- https://git.kernel.org/stable/c/c401492e01c7bfd38cf14c94d85c7efafe7d1a25
- https://git.kernel.org/stable/c/e4b7b9819811c4c51064c3d3d3c02f0be7491707
- https://git.kernel.org/stable/c/ee2458f8188732aa53a5d42f56e87bfad288b44e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74438.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74438
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
