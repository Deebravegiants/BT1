# [H] netfilter: nft_set_pipapo: don't leak bad clone into future transaction

## Summary
Severity: High
Advisory: CVE-2026-72252
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72252
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.148, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_set_pipapo: don't leak bad clone into future transaction

On memory allocation failure the cloned nft_pipapo_match can enter a bad
state:
 - some fields can have their lookup tables resized while others did
   not
 - bits might have been toggled
 - scratch map can be undersized which also means m->bsize_max can be
   lower than what is required

This means that the next insertion in the same batch can trigger
out-of-bounds writes.

Furthermore, a failure in the first can result in the bad clone to
leak into the next transaction because the abort callback is never
executed in this case (the upper layer saw an error and no attempt to
allocate a transactional request was made).

Record a state for the nft_pipapo_match structure:
- NEW (pristine clone)
- MOD (modified clone with good state)
- ERR (potentially bogus content)

Then make it so that deletes and insertions fail when the clone
entered ERR state.

In case the very first insert attempt results in an error, free the
clone right away.

## References
- https://git.kernel.org/stable/c/02b6b0e892aea582590671796fd6eff5b93ea93f
- https://git.kernel.org/stable/c/047e813324eac2ac60cddfb58bcdbd0144eadb09
- https://git.kernel.org/stable/c/0ab7b1802f63ca5b288ea59acb467830b83abd6b
- https://git.kernel.org/stable/c/47e65eff50691f0a5b79d325e28d83ec1da43bcf
- https://git.kernel.org/stable/c/610e3b73efaec3dd81a95dcda2421ad7d9795bd0
- https://git.kernel.org/stable/c/cc53703f48558896295f565cd4f5e956d21b7af4
- https://git.kernel.org/stable/c/e74f9680e1b64872a51cc7b5bda1edaaa08aa51f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72252.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72252
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
