# [M] Vitess vulnerable to infinite memory consumption and vtgate crash

## Summary
Severity: Medium
Advisory: GHSA-649x-hxfx-57j2
CVE: CVE-2024-32886
CWE: CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-08
Source: https://github.com/advisories/GHSA-649x-hxfx-57j2
Type: github-advisory

## Affected
- Go: `github.com/vitessio/vitess` — affected >=19.0.0 <19.0.4
- Go: `github.com/vitessio/vitess` — affected >=18.0.0 <18.0.5
- Go: `github.com/vitessio/vitess` — affected >=0 <17.0.7
- Go: `vitess.io/vitess` — affected >=0 <0.17.7
- Go: `vitess.io/vitess` — affected >=0.18.0 <0.18.5
- Go: `vitess.io/vitess` — affected >=0.19.0 <0.19.4

## Details
### Summary

When executing the following simple query, the `vtgate` will go into an endless loop that also keeps consuming memory and eventually will OOM.

### Details

When running the following query, the `evalengine` will try evaluate it and runs forever.

```
select _utf16 0xFF
```

The source of the bug lies in the collation logic that we have. The bug applies to all `utf16`,  `utf32` and `ucs2` encodings.  In general, the bug is there for any encoding where the minimal byte length for a single character is more than 1 byte.

The decoding functions for these collations all implement logic like the following to enforce the minimal character length:

https://github.com/vitessio/vitess/blob/8f6cfaaa643a08dc111395a75a2d250ee746cfa8/go/mysql/collations/charset/unicode/utf16.go#L69-L71

The problem is that all the callers of `DecodeRune` expect progress by returning the number of bytes consumed. This means that if there's only 1 byte left in an input, it will here return still `0` and the caller(s) don't consume the character. 

One example of such a caller is the following:

https://github.com/vitessio/vitess/blob/8f6cfaaa643a08dc111395a75a2d250ee746cfa8/go/mysql/collations/charset/convert.go#L73-L79

The logic here moves forward the pointer in the input `[]byte` but if `DecodeRune` returns `0` in case of error, it will keep running forever. The OOM happens since it keeps adding the `?` as the invalid character to the destination buffer infinitely, growing forever until it runs out of memory.

The fix here would be to always return forward progress also on invalid strings. 

There's also a separate bug here that even if progress is guaranteed, `select _utf16 0xFF` will return the wrong result currently. MySQL will pad here the input when the `_utf16` introducer is used with leading `0x00` bytes and then decode to UTF-16, resulting in the output of `ÿ` here. 

### PoC

```
select _utf16 0xFF
```

### Impact

Denial of service attack by triggering unbounded memory usage.

## References
- https://github.com/vitessio/vitess/security/advisories/GHSA-649x-hxfx-57j2
- https://nvd.nist.gov/vuln/detail/CVE-2024-32886
- https://github.com/vitessio/vitess/commit/2fd5ba1dbf6e9b32fdfdaf869d130066b1b5c0df
- https://github.com/vitessio/vitess/commit/9df4b66550e46b5d7079e21ed0e1b0f49f92b055
- https://github.com/vitessio/vitess/commit/c46dc5b6a4329a10589ca928392218d96031ac8d
- https://github.com/vitessio/vitess/commit/d438adf7e34a6cf00fe441db80842ec669a99202
- https://github.com/vitessio/vitess
- https://github.com/vitessio/vitess/blob/8f6cfaaa643a08dc111395a75a2d250ee746cfa8/go/mysql/collations/charset/convert.go#L73-L79
- https://github.com/vitessio/vitess/blob/8f6cfaaa643a08dc111395a75a2d250ee746cfa8/go/mysql/collations/charset/unicode/utf16.go#L69-L71
