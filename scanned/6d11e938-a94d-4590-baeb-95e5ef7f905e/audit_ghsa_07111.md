# [M] veraPDF Parser DoS via PostScript Type 1 Font Programs

## Summary
Severity: Medium
Advisory: GHSA-7c26-995w-6f47
CVE: CVE-2026-54081
CWE: CWE-1325
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-7c26-995w-6f47
Type: github-advisory

## Affected
- Maven: `org.verapdf:parser` — affected >=0 <1.30.2
- Maven: `org.verapdf:parser` — affected >=1.31.1 <1.31.23

## Details
## Summary

**Description**

A PostScript-interpreter-driven Denial of Service (CWE-1325) vulnerability in veraPDF allows a remote attacker to exhaust validator memory or CPU by submitting a PDF whose Type 1 font `/FontFile` is a font program containing attacker-supplied PostScript. veraPDF's Type 1 font program parser dispatches every cleartext token through a hardcoded operator allow-list whose members include the unbounded `array N` allocation operator and the `for` control operator with no zero-increment guard. This affects all current versions of veraPDF-parser.

## Details

The vulnerability resides in veraPDF-parser. Type 1 font program streams referenced from any Type 1 font's `/FontDescriptor /FontFile` are parsed by `Type1FontProgram` (veraPDF-parser/src/main/java/org/verapdf/pd/font/type1/Type1FontProgram.java), which extends `PSParser`. `parseFont` reads cleartext PostScript tokens until it encounters `eexec` (which switches into the encrypted private dictionary parser) or end-of-stream. Each non-`eexec` token is dispatched via `toExecute`, which gates execution behind a hardcoded allow-list.

The allow-list explicitly admits both `ARRAY` (Type1FontProgram.java:98) and `FOR` (Type1FontProgram.java:100). When either keyword passes the gate, `operator.execute` delegates straight into the generic `PSOperator` implementation (`org.verapdf.parser.postscript.PSOperator`, methods `array()` at PSOperator.java:536-547 and `opFor()` at PSOperator.java:571-592), which apply no validation:

1. `array N` calls `COSArray.construct(N)` followed by `new ArrayList<>(N)` (COSArray.java:102), so the underlying `Object[]` is allocated up-front. Passing `2147483647` (`Integer.MAX_VALUE`) requests a 16 GB backing array on a 64-bit JVM.
2. `for` runs `for (long i = initial; i <= limit; i += increment)` with no validation of `increment`. With `increment == 0`, the loop never exits.

In addition to the two shared primitives, `toExecute` introduces a third primitive specific to this code path: when an unknown operator is encountered, it looks the name up in `userDict` and recursively re-executes the value. There is no visited-set, no recursion-depth cap, and no detection of a cycle. A Type 1 font program that defines a name to itself, such as `/loop { loop } def loop`, recurses indefinitely on the JVM stack and throws `StackOverflowError` after ~16,000 frames.

The interpreter is reachable on every Type 1 font validation. `GFPDType1Font`'s constructor unconditionally calls `program.parseFont()`.

`Type1FontProgram.parseFont` only catches `PostScriptException` and rewraps it as `IOException`; it does not catch `OutOfMemoryError`, `StackOverflowError`, or wall-clock budget, so any of the three failure modes propagates out of font model construction and aborts the validation worker.

A single payload byte sequence is sufficient. The conventional `%!PS-AdobeFont-1.0` header line is treated as a comment and skipped; the parser then begins consuming PostScript tokens, the very first `for` invocation enters the infinite loop, and the parser never reaches the `eexec` boundary that would normally end the cleartext section.

## Impact

This impacts all current releases of the veraPDF-parser. Successful exploitation requires only that the target validate an attacker-supplied PDF; a single Type 1 font with a malicious `/FontFile` stream is sufficient.

## References
- https://github.com/veraPDF/veraPDF-parser/security/advisories/GHSA-7c26-995w-6f47
- https://github.com/veraPDF/veraPDF-parser/pull/703
- https://github.com/veraPDF/veraPDF-parser/commit/73d6ec002b98ce1f3f68640442f8e5d5613c80ce
- https://github.com/veraPDF/veraPDF-parser/commit/cb3538607a549d63504299be1088c85ae48605f4
- https://github.com/veraPDF/veraPDF-parser
