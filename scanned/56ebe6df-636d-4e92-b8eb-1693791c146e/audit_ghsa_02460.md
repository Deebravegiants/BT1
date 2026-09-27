# [C] Memory corruption slice-deque

## Summary
Severity: Critical
Advisory: GHSA-hr3c-6mmp-6m39
CVE: CVE-2018-20995
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-hr3c-6mmp-6m39
Type: github-advisory

## Affected
- crates.io: `slice-deque` — affected >=0 <0.1.16

## Details
Affected versions of this crate did not properly update the head and tail of the deque when inserting and removing elements from the front if, before insertion or removal, the tail of the deque was in the mirrored memory region, and if, after insertion or removal, the head of the deque is exactly at the beginning of the mirrored memory region.

An attacker that controls both element insertion and removal into the deque could put it in a corrupted state. Once the deque enters such an state, its head and tail are corrupted, but in bounds of the allocated memory. This can result in partial reads and writes, reads of uninitialized memory, reads of memory containing previously dropped objects, etc. An attacker could exploit this to alter program execution.

The flaw was corrected by properly updating the head and tail of the deque in this case.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20995
- https://github.com/gnzlbg/slice_deque/issues/57
- https://github.com/gnzlbg/slice_deque
- https://rustsec.org/advisories/RUSTSEC-2018-0008.html
