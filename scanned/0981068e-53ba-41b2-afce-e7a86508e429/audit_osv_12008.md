# [M] CVE-2018-1000636

## Summary
Severity: Medium
Advisory: CVE-2018-1000636
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000636
Type: osv

## Details
JerryScript version Tested on commit f86d7459d195c8ba58479d1861b0cc726c8b3793. Analysing history it seems that the issue has been present since commit 64a340ffeb8809b2b66bbe32fd443a8b79fdd860 contains a CWE-476: NULL Pointer Dereference vulnerability in Triggering undefined behavior at jerry-core/ecma/builtin-objects/typedarray/ecma-builtin-typedarray-prototype.c:598 (passing NULL to memcpy as 2nd argument) results in null pointer dereference (segfault) at jerry-core/jmem/jmem-heap.c:463 that can result in Crash due to segmentation fault. This attack appear to be exploitable via The victim must execute specially crafted javascript code. This vulnerability appears to have been fixed in after commit 87897849f6879df10e8ad68a41bf8cf507edf710.

## References
- https://github.com/jerryscript-project/jerryscript/issues/2435
