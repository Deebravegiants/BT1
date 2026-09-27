# [C] netfilter: nft_set_pipapo_avx2: don't return non-matching entry on expiry

## Summary
Severity: Critical
Advisory: CVE-2026-43114
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43114
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_set_pipapo_avx2: don't return non-matching entry on expiry

New test case fails unexpectedly when avx2 matching functions are used.

The test first loads a ranomly generated pipapo set
with 'ipv4 . port' key, i.e.  nft -f foo.

This works.  Then, it reloads the set after a flush:
(echo flush set t s; cat foo) | nft -f -

This is expected to work, because its the same set after all and it was
already loaded once.

But with avx2, this fails: nft reports a clashing element.

The reported clash is of following form:

    We successfully re-inserted
      a . b
      c . d

Then we try to insert a . d

avx2 finds the already existing a . d, which (due to 'flush set') is marked
as invalid in the new generation.  It skips the element and moves to next.

Due to incorrect masking, the skip-step finds the next matching
element *only considering the first field*,

i.e. we return the already reinserted "a . b", even though the
last field is different and the entry should not have been matched.

No such error is reported for the generic c implementation (no avx2) or when
the last field has to use the 'nft_pipapo_avx2_lookup_slow' fallback.

Bisection points to
7711f4bb4b36 ("netfilter: nft_set_pipapo: fix range overlap detection")
but that fix merely uncovers this bug.

Before this commit, the wrong element is returned, but erronously
reported as a full, identical duplicate.

The root-cause is too early return in the avx2 match functions.
When we process the last field, we should continue to process data
until the entire input size has been consumed to make sure no stale
bits remain in the map.

## References
- https://git.kernel.org/stable/c/07de44424bb7f17ef9357e8535df96d9e97c40cb
- https://git.kernel.org/stable/c/0abbc43f71d99baadeeba6fa3fe1c80b676f57ed
- https://git.kernel.org/stable/c/1c43f0dd8691ddf8884793b481ddc7511cf593c3
- https://git.kernel.org/stable/c/3d53f9aafd469ae1ea27051e00f5b96ca1b55d52
- https://git.kernel.org/stable/c/c7babe2f28b507e17f28e9f753b7caec72d4857f
- https://git.kernel.org/stable/c/d3c0037ffe1273fa1961e779ff6906234d6cf53c
- https://git.kernel.org/stable/c/f8c39983fc9c1a978c82e6f2df7bfba8a8561587
- https://git.kernel.org/stable/c/fa4f1f52528c73989d820f32bfca06bec5afeece
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43114.json
- https://access.redhat.com/errata/RHSA-2026:59723
- https://access.redhat.com/errata/RHSA-2026:62568
- https://access.redhat.com/errata/RHSA-2026:62638
- https://access.redhat.com/errata/RHSA-2026:62639
- https://access.redhat.com/errata/RHSA-2026:62640
- https://access.redhat.com/errata/RHSA-2026:62641
- https://access.redhat.com/errata/RHSA-2026:62642
- https://access.redhat.com/errata/RHSA-2026:63093
- https://access.redhat.com/errata/RHSA-2026:64767
- https://access.redhat.com/errata/RHSA-2026:65712
- https://access.redhat.com/security/cve/CVE-2026-43114
