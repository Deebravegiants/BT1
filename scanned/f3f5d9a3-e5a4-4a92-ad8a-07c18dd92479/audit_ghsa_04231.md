# [H] Oj: Stack Buffer Overflow in Oj::Doc#each_child via Deeply Nested Input

## Summary
Severity: High
Advisory: GHSA-3m6q-jj5j-38c9
CVE: CVE-2026-54592
CWE: CWE-125, CWE-787
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-3m6q-jj5j-38c9
Type: github-advisory

## Affected
- RubyGems: `oj` — affected >=0 <3.17.3

## Details
### Summary

`Oj::Doc#each_child`, when invoked recursively over a deeply nested JSON
document, overflows a fixed-size stack buffer and aborts the process. This is a
denial of service reachable from untrusted JSON.

### Details

Two-step chain in `ext/oj/fast.c`:

1. **`doc_each_child` (~line 1501)** increments `doc->where` past the
   `where_path[MAX_STACK = 100]` array with no bounds check, and never restores
   it (`doc->where--` is missing). Calling `each_child` recursively from inside
   the yield block therefore drives `doc->where` beyond the array.

2. **On the next entry (~line 1478)** the function copies the path into a
   stack-local buffer:

   ```c
   Leaf  save_path[MAX_STACK];           // 800-byte stack buffer
   size_t wlen = doc->where - doc->where_path;
   if (0 < wlen) {
       memcpy(save_path, doc->where_path, sizeof(Leaf) * (wlen + 1));
   }
   ```

   When the previous recursive call left `doc->where` past `where_path[100]`,
   `wlen` exceeds `MAX_STACK` and the `memcpy` overflows `save_path` on the C
   stack.

The `Oj::Doc` parser imposes no JSON nesting-depth limit (it relies on a
C-stack pressure check), so deeply nested attacker input reaches this path.

### Proof of Concept

```ruby
require 'oj'
depth = 200
payload = '[' * depth + '1' + ']' * depth
Oj::Doc.open(payload) do |doc|
  r = lambda { doc.each_child { |_| r.call } }
  r.call
end
```

Recursion depth <= 99 iterates normally; depth >= 101 aborts. lldb backtrace
on the affected build (`ruby 3.3.8 / arm64-darwin24`):

```
SIGABRT
#2 __abort
#3 __stack_chk_fail
#4 doc_each_child   (oj.bundle, fast.c)
```

### Impact

Reliable denial of service: any endpoint that calls
`Oj::Doc.open(untrusted) { |d| d.each_child ... }` recursively can be crashed
with a small deeply-nested payload. On builds with a stack protector (the
default, `-fstack-protector-strong`) the canary aborts the process before the
saved return address is used. The Step-1 heap OOB writes into `struct _doc`
fields do occur, but are masked in practice because the Step-2 stack overflow
crashes first; turning them into anything beyond a crash has not been
demonstrated.

### Patches

Fixed in **3.17.3**: `doc_each_child` now bounds-checks before incrementing
`doc->where` (raising `Oj::DepthError`) and restores `doc->where` after the
loop, matching the existing `each_leaf` pattern. Verified on the fixed build:
depth >= 101 raises a clean `Oj::DepthError` instead of aborting.

### Credit

Reported by Zac Wang (@7a6163).

## References
- https://github.com/ohler55/oj/security/advisories/GHSA-3m6q-jj5j-38c9
- https://github.com/ohler55/oj
