# [H] block: don't overwrite bip_vcnt in bio_integrity_copy_user()

## Summary
Severity: High
Advisory: CVE-2026-64053
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64053
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: don't overwrite bip_vcnt in bio_integrity_copy_user()

bio_integrity_add_page() already sets bip_vcnt to 1 for the bounce
segment. Overwriting it with nr_vecs breaks bip_vcnt <= bip_max_vcnt
on WRITE (bip_max_vcnt is 1), so the gap-merge checks in block/blk.h
read past the bip_vec[] flex array. On READ the read is in bounds
but lands on a saved user bvec instead of the bounce.

The line was added for split propagation, but bio_integrity_clone()
doesn't copy bip_vcnt and BIP_CLONE_FLAGS excludes BIP_COPY_USER.

## References
- https://git.kernel.org/stable/c/066be1439593a381b1a29663becfcfe0c92363e7
- https://git.kernel.org/stable/c/0d48654af4d1390c888389206cc13b51b82c30e6
- https://git.kernel.org/stable/c/637ad3a56a3b889527d1dacea6fea2a8bd648140
- https://git.kernel.org/stable/c/d18160c9525c63c203656fefd847e94b538cd4a4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64053.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64053
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
