# [H] Oj: Use-After-Free in Oj::Parser Symbol Key Cache Toggle

## Summary
Severity: High
Advisory: GHSA-2cw7-v8ff-p88r
CVE: CVE-2026-54899
CWE: CWE-416
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-2cw7-v8ff-p88r
Type: github-advisory

## Affected
- RubyGems: `oj` — affected >=0 <3.17.3

## Details
### Summary

Disabling `symbol_keys` on a reused `Oj::Parser` instance triggers a heap use-after-free. When `symbol_keys` is toggled from `true` to `false`, `opt_symbol_keys_set` frees the internal key cache (`cache_free`) but does not clear the pointer. The next `parse` call reads from the freed cache via `cache_intern`, producing a use-after-free.

### Version

- **Software**: oj gem
- **Affected**: all versions with `ext/oj/usual.c`
- **Latest tested**: 3.17.1 (confirmed present)

### Details

`ext/oj/usual.c`, `opt_symbol_keys_set`:

```c
// usual.c:1043–1051
if (symbol_keys) {
    d->key_cache = cache_create(...);   // allocate
} else {
    cache_free(d->key_cache);           // free — but d->key_cache pointer not NULLed
}
```

On the next parse call, `cache_key` → `cache_intern` reads from `d->key_cache` which now points to freed memory.

ASAN report:
```
==145265==ERROR: AddressSanitizer: heap-use-after-free on address 0x50b00001a318
READ of size 8 at 0x50b00001a318 thread T0
    #0 cache_intern            /ext/oj/cache.c:328
    #1 cache_key               /ext/oj/usual.c:161
    #2 close_object            /ext/oj/usual.c:285
    #3 parse                   /ext/oj/parser.c:693
    #4 parser_parse            /ext/oj/parser.c:1408
freed by thread T0 here:
    #0 free
    #1 cache_free              /ext/oj/cache.c:277
    #2 opt_symbol_keys_set     /ext/oj/usual.c:1051
    #3 option                  /ext/oj/usual.c:1111
    #4 parser_missing          /ext/oj/parser.c:1362
0x50b00001a318 is 40 bytes inside freed 112-byte region [fd]fd fd fd fd fd fd fd
```

### Reproduce

```ruby
require 'oj'
p = Oj::Parser.new(:usual, symbol_keys: true)
p.symbol_keys = false     # frees cache without nulling pointer
p.parse('{"attacker":1}') # UAF: reads freed cache
```

## References
- https://github.com/ohler55/oj/security/advisories/GHSA-2cw7-v8ff-p88r
- https://github.com/ohler55/oj
