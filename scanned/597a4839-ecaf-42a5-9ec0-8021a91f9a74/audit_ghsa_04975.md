# [H] Oj: Use-After-Free in Oj::Parser array_class/hash_class GC Marking

## Summary
Severity: High
Advisory: GHSA-vwm4-62gf-x745
CVE: CVE-2026-54901
CWE: CWE-416
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-vwm4-62gf-x745
Type: github-advisory

## Affected
- RubyGems: `oj` — affected >=0 <3.17.3

## Details
### Summary

`Oj::Parser` in usual mode does not mark `array_class` and `hash_class` references during garbage collection. If GC runs after the class is assigned but before a parse, the class object is reclaimed, leaving the parser holding a dangling VALUE. The subsequent `parse` call dereferences the freed object, producing a segfault.

### Version

- **Software**: oj gem
- **Affected**: all versions with `ext/oj/usual.c` / `ext/oj/parser.c`
- **Latest tested**: 3.17.1 (confirmed present)

### Details

The `parser_mark` function in `ext/oj/parser.c` is registered as the GC mark callback for the parser's `TypedData`. If `array_class` (stored as `d->array_class` in the `Usual` struct) is not passed to `rb_gc_mark`, the GC does not know it is referenced and may collect it.

When `close_array_class` (`usual.c:405`) later calls `rb_funcallv` on the collected class VALUE, it accesses freed memory, crashing at `RIP: 0x7f... / 0x0000000000000000`.

Crash output:
```
array_class finalized
about to parse
[BUG] Segmentation fault at 0x0000000000000000
    close_array_class+0x194  /ext/oj/usual.c:405
    parse+0x17b3             /ext/oj/parser.c:715
    parser_parse+0x10b       /ext/oj/parser.c:1408
RIP: 0x7fd1b46d68b7  RBP: 0x0000000000000000
```

### Reproduce

```ruby
require 'oj'
p = Oj::Parser.new(:usual,
  array_class: (ac = Class.new { def <<(_x); end }))
ObjectSpace.define_finalizer(ac, proc { warn 'array_class finalized' })
ac = nil
GC.start(full_mark: true, immediate_sweep: true)  # collect the class
p.parse('[1]')  # segfault
```

## References
- https://github.com/ohler55/oj/security/advisories/GHSA-vwm4-62gf-x745
- https://github.com/ohler55/oj
