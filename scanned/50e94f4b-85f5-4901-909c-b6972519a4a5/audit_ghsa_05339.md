# [H] Oj: Stack Buffer Overflow in Oj.dump via Large Indent

## Summary
Severity: High
Advisory: GHSA-3v45-f3vh-wg7m
CVE: CVE-2026-54502
CWE: CWE-121
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-3v45-f3vh-wg7m
Type: github-advisory

## Affected
- RubyGems: `oj` — affected >=0 <3.17.3

## Details
### Summary

`Oj.dump` is vulnerable to a stack-based buffer overflow when a large `:indent` value is provided by the developer. `fill_indent` in `dump.h` calls `memset(indent_str, ' ', (size_t)opts->indent)` without validating the size. When `opts->indent` is set to `INT_MAX` (2,147,483,647), the `(size_t)` cast preserves the large value and `memset` writes 2 GB into the stack-allocated `out` buffer (4,184 bytes), corrupting the stack and crashing the process.

### Version

- **Software**: oj gem
- **Affected**: all versions with `ext/oj/dump.h`
- **Latest tested**: 3.17.1 (confirmed present)

### Details

`ext/oj/dump.h`, line 77:

```c
static void fill_indent(Out out, int depth) {
    if (0 < out->opts->indent) {
        size_t len = (size_t)(out->opts->indent * depth);
        // ...
        memset(out->buf + ..., ' ', len);  // len = 2147483647 * depth
```

The `indent` option is accepted as a plain Ruby integer and stored as `int` without range validation. Multiplying by `depth` can produce a value larger than any stack or heap buffer.

ASAN report:
```
==69820==ERROR: AddressSanitizer: stack-buffer-overflow on address 0x7fd1fc201278
WRITE of size 2147483647 at 0x7fd1fc201278 thread T0
    #0 memset
    #1 fill_indent  /ext/oj/dump.h:77
    #2 dump_array   /ext/oj/dump_compat.c:165
    #3 oj_dump_obj_to_json_using_params  /ext/oj/dump.c:818
    #4 dump_body    /ext/oj/oj.c:1429
    #5 dump         /ext/oj/oj.c:1480
Address is in stack of thread T0 at offset 4728 in frame:
    #0 dump /ext/oj/oj.c:1453
  [544, 4728) 'out'  <== Memory access at offset 4728 overflows this variable
```

### Reproduce

```ruby
require "oj"
obj = [0]
Oj.dump(obj, mode: :compat, indent: 2_147_483_647)
```

### Workaround

The develop should not use extreme indents and should not offer the option for users to dump Ruby data with unlimited indentation size.

## References
- https://github.com/ohler55/oj/security/advisories/GHSA-3v45-f3vh-wg7m
- https://github.com/ohler55/oj
