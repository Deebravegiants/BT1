# [H] Integer overflow in memalign leads to heap corruption

## Summary
Severity: High
Advisory: CVE-2026-0861
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2026-0861
Type: osv

## Details
Passing too large an alignment to the memalign suite of functions (memalign, posix_memalign, aligned_alloc) in the GNU C Library version 2.30 to 2.42 may result in an integer overflow, which could consequently result in a heap corruption.

Note that the attacker must have control over both, the size as well as the alignment arguments of the memalign function to be able to exploit this.  The size parameter must be close enough to PTRDIFF_MAX so as to overflow size_t along with the large alignment argument.  This limits the malicious inputs for the alignment for memalign to the range [1<<62+ 1, 1<<63] and exactly 1<<63 for posix_memalign and aligned_alloc.

Typically the alignment argument passed to such functions is a known constrained quantity (e.g. page size, block size, struct sizes) and is not attacker controlled, because of which this may not be easily exploitable in practice.  An application bug could potentially result in the input alignment being too large, e.g. due to a different buffer overflow or integer overflow in the application or its dependent libraries, but that is again an uncommon usage pattern given typical sources of alignments.

## References
- http://www.openwall.com/lists/oss-security/2026/01/16/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0861.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0861
- https://sourceware.org/git/?p=glibc.git;a=blob_plain;f=advisories/GLIBC-SA-2026-0001
- https://sourceware.org/bugzilla/show_bug.cgi?id=33796
