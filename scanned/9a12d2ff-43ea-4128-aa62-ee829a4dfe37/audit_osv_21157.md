# [H] CVE-2021-40941

## Summary
Severity: High
Advisory: CVE-2021-40941
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2021-40941
Type: osv

## Details
In Bento4 1.6.0-638, there is an allocator is out of memory in the function AP4_Array<AP4_TrunAtom::Entry>::EnsureCapacity in Ap4Array.h:172, as demonstrated by GPAC. This can cause a denial of service (DOS).

## References
- https://github.com/axiomatic-systems/Bento4/issues/644
