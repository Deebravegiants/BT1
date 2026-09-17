# [C] md/raid10: reset read_slot when reusing r10bio for discard

## Summary
Severity: Critical
Advisory: CVE-2026-74376
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74376
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/raid10: reset read_slot when reusing r10bio for discard

put_all_bios() always drops devs[i].bio, but it only drops
devs[i].repl_bio when r10_bio->read_slot < 0. If discard reuses an
r10bio that was previously used for a read, read_slot can still be
non-negative, and discard cleanup can skip bio_put() on repl_bio.

Reset read_slot to -1 when preparing an r10bio for discard so the
replacement bio is always released correctly.

## References
- https://git.kernel.org/stable/c/3cb2a606ce4902eceabe68338df0653312f861f8
- https://git.kernel.org/stable/c/561c9711e4f545d6464a023168bdee03b00fa945
- https://git.kernel.org/stable/c/6b8a26af065ddc93de2aa5c9f0df98dce9723442
- https://git.kernel.org/stable/c/742e4afd247d9c972695227716b03d432a7e1d26
- https://git.kernel.org/stable/c/b7313f23ea5a79b199a007bfad64a866cc2c22e7
- https://git.kernel.org/stable/c/ce3030e92f14362880055de5fe3c258971118853
- https://git.kernel.org/stable/c/eb04e3e9c14ed15914f5fd2eae8b6435f54f095f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74376.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74376
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
