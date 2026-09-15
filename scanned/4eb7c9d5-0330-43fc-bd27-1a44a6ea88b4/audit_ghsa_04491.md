# [H] Oj: Use-After-Free in Oj::Parser SAJ Long Key Callback

## Summary
Severity: High
Advisory: GHSA-m578-w5vf-rfcm
CVE: CVE-2026-54902
CWE: CWE-416
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-m578-w5vf-rfcm
Type: github-advisory

## Affected
- RubyGems: `oj` — affected >=0 <3.17.3

## Details
### Summary

`Oj::Parser` in SAJ mode does not protect cached object keys (≥ 35 bytes) from garbage collection. A Ruby callback that triggers GC inside `hash_end` can cause the key string to be reclaimed while the C parser still holds a pointer to it. The subsequent access to the freed string VALUE results in a segfault, confirmed by an RIP pointing to address `0x4242` (a canary-style pattern suggesting control over the freed memory's content).

### Version

- **Software**: oj gem
- **Affected**: all versions with `ext/oj/saj2.c` / `ext/oj/parser.c`
- **Latest tested**: 3.17.1 (confirmed present)

### Details

Short keys (≤ 34 bytes) are stored inline on the C stack and are safe. Long keys (≥ 35 bytes) are stored as heap-allocated Ruby String objects passed to `rb_funcall` as the `key` argument. Between the key being resolved and the callback completing, a GC triggered inside the callback (e.g. `GC.start`) can collect the key String, leaving a dangling VALUE.

Crash output:
```
long_key_trigger
[BUG] Segmentation fault at 0x0000000000004242
    close_object+0x260    /ext/oj/usual.c:405  (calls rb_funcall with freed key)
    parse+0x11ff          /ext/oj/parser.c:693
    parser_parse+0x145    /ext/oj/parser.c:1408

RIP: 0x7fd1b46d68b7  RDI: 0x0000000000004242  (freed key VALUE)
R12: 0x0000000000004242
```

The freed VALUE `0x4242` shows the attacker-controlled content of the key string was loaded as a pointer — a classic use-after-free indicator.

### Reproduce

```ruby
require 'oj'

class H < Oj::Saj
  def add_value(value, key)
    GC.start(full_mark: true, immediate_sweep: true) if key == 'x'
  end
  def hash_start(key); end
  def hash_end(key); end
end

p = Oj::Parser.new(:saj)
p.handler = H.new
p.parse('{"' + 'A' * 35 + '":{"x":1}}')  # long outer key, GC fires on inner key
```

## References
- https://github.com/ohler55/oj/security/advisories/GHSA-m578-w5vf-rfcm
- https://github.com/ohler55/oj
