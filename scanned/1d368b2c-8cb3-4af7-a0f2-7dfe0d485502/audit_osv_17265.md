# [H] CVE-2020-14163

## Summary
Severity: High
Advisory: CVE-2020-14163
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-15
Source: https://osv.dev/vulnerability/CVE-2020-14163
Type: osv

## Details
An issue was discovered in ecma/operations/ecma-container-object.c in JerryScript 2.2.0. Operations with key/value pairs did not consider the case where garbage collection is triggered after the key operation but before the value operation, as demonstrated by improper read access to memory in ecma_gc_set_object_visited in ecma/base/ecma-gc.c.

## References
- https://github.com/jerryscript-project/jerryscript/issues/3804
- https://github.com/jerryscript-project/jerryscript/commit/c2b662170245a16f46ce02eae68815c325d99821
