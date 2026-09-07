# [M] Oj: intern.c form_attr (uninitialized stack read)

## Summary
Severity: Medium
Advisory: GHSA-fm7p-mprw-wjm9
CVE: CVE-2026-54500
CWE: CWE-125, CWE-908
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-fm7p-mprw-wjm9
Type: github-advisory

## Affected
- RubyGems: `oj` — affected >=0 <3.17.3

## Details
### Summary

`Oj.load` in `:object` mode reads uninitialized stack memory (and, for long
keys, reads out of bounds) when parsing a JSON object whose key is 254 bytes
or longer. The interned bytes can surface to the caller, disclosing process
stack memory.

### Details

In `ext/oj/intern.c`, `form_attr()` handles the long-key path by allocating a
heap buffer `b`, populating it with the attribute name, and then freeing it —
but it passed the **uninitialized stack buffer `buf`** (not `b`) to
`rb_intern3()`:

```c
static VALUE form_attr(const char *str, size_t len) {
    char buf[256];
    if (sizeof(buf) - 2 <= len) {        // long-key path (len >= 254)
        char *b = OJ_R_ALLOC_N(char, len + 2);
        // ... b is filled correctly ...
        id = rb_intern3(buf, len + 1, oj_utf8_encoding);   // BUG: reads `buf`
        OJ_R_FREE(b);
        return id;
    }
    // ...
}
```

`rb_intern3` therefore reads `len + 1` bytes of uninitialized stack memory.
When the key length is >= 256, it also reads out of bounds past the 256-byte
`buf` (CWE-125). The resulting bytes are interned and can reach the caller via
the produced Symbol or via the `EncodingError` message raised on invalid
UTF-8, leaking process stack contents.

This is the same defect previously fixed in `ext/oj/usual.c`; `intern.c` held
a duplicated copy of `form_attr` that was missed.

### Proof of Concept

```ruby
require 'oj'
key  = "A" * 300
json = %Q[{"^o":"Object","#{key}":1}]
Oj.load(json, mode: :object)
```

On affected versions this raises an `EncodingError` whose message contains
~1500 bytes of uninitialized stack memory (not the supplied "A"s). The leaked
byte count varies between runs with the identical payload (e.g. 1491 vs 1516
bytes), confirming the content is uninitialized memory rather than fixed data.

### Impact

Information disclosure of process stack memory to a caller that parses
untrusted JSON with `Oj.load(..., mode: :object)`. For keys >= 256 bytes it is
also an out-of-bounds read (CWE-125).

Severity is bounded by several preconditions: it requires `:object` mode
(which is already discouraged for untrusted input), the leaked bytes are
uncontrolled (the attacker cannot choose what is disclosed), and the data only
reaches an attacker if the application surfaces the resulting Symbol or
`EncodingError` back to them. Scored CVSS 5.3 (Medium) on that basis.

### Patches

Fixed in **3.17.3**: `form_attr()` now passes `b` to `rb_intern3` (a
one-character change mirroring the earlier `usual.c` fix). Verified on the
fixed build: the same payload returns cleanly with no leak across repeated
runs.

### Credit

Reported by Zac Wang (@7a6163).

## References
- https://github.com/ohler55/oj/security/advisories/GHSA-fm7p-mprw-wjm9
- https://github.com/ohler55/oj
