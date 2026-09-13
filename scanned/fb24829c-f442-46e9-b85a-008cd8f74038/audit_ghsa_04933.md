# [H] Oj: Heap Buffer Overflow in Oj.dump Exception Serialization via Large Indent

## Summary
Severity: High
Advisory: GHSA-35w3-pjm6-wj95
CVE: CVE-2026-54896
CWE: CWE-122
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-35w3-pjm6-wj95
Type: github-advisory

## Affected
- RubyGems: `oj` — affected >=0 <3.17.3

## Details
### Summary

`Oj.dump` in object mode is vulnerable to a heap buffer overflow when serializing Exception objects with a large `:indent` value. The serializer allocates a buffer sized for the object's attributes but does not account for the indent bytes added on each write. With `indent: 5000`, the accumulation of 5,000-byte indent strings overflows the 13,150-byte heap allocation, corrupting adjacent heap memory.

### Version

- **Software**: oj gem
- **Affected**: all versions with `ext/oj/dump.h`
- **Latest tested**: 3.17.1 (confirmed present)

### Details

`ext/oj/dump.h`, line 75–77:

```c
static void fill_indent(Out out, int depth) {
    if (0 < out->opts->indent) {
        memset(out->buf + out->cur, ' ', (size_t)(out->opts->indent * depth));
```

When dumping an Exception object in `:object` mode, `dump_obj_attrs` calls `fill_indent` repeatedly for each attribute. The buffer is pre-allocated based on the serialized content but not the indentation overhead. With `indent: 5000` the indent block for a nested object exceeds the remaining buffer space, producing a heap-buffer-overflow of size 5,000 at the end of the allocated region.

ASAN report:
```
==101656==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x527000022c5e
WRITE of size 5000 at 0x527000022c5e thread T0
    #0 memset
    #1 fill_indent       /ext/oj/dump.h:77
    #2 dump_obj_attrs    /ext/oj/dump_object.c:552
    #3 dump_obj          /ext/oj/dump_object.c:80
    #4 oj_dump_obj_val   /ext/oj/dump_object.c:708
    #5 oj_dump_obj_to_json_using_params  /ext/oj/dump.c:817
    #6 dump_body         /ext/oj/oj.c:1429
    #7 dump              /ext/oj/oj.c:1480
0x527000022c5e is located 0 bytes after 13150-byte region [0x52700001f900, 0x527000022c5e)
```

### Reproduce

```ruby
require "oj"
obj = Oj.load('{"^o":"RuntimeError"}', mode: :object)
Oj.dump(obj, mode: :object, indent: 5000)
```

### Workarounds

This is at the discretion of the developer and not a public facing option so the workaround is the develop should not use extreme indents and should not offer the option for users to dump Ruby data with unlimited indentation size.

## References
- https://github.com/ohler55/oj/security/advisories/GHSA-35w3-pjm6-wj95
- https://github.com/ohler55/oj
