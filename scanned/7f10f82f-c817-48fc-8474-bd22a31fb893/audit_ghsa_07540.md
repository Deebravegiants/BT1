# [M] veraPDF Parser DoS via PostScript CMap Streams

## Summary
Severity: Medium
Advisory: GHSA-jrmc-qg6p-94fp
CVE: CVE-2026-54080
CWE: CWE-1325
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-jrmc-qg6p-94fp
Type: github-advisory

## Affected
- Maven: `org.verapdf:parser` — affected >=0 <1.30.2
- Maven: `org.verapdf:parser` — affected >=1.31.1 <1.31.23

## Details
## Summary

**Description**

A PostScript-interpreter-driven Denial of Service (CWE-1325) vulnerability in veraPDF allows a remote attacker to exhaust validator memory or CPU by submitting a PDF whose Type 0 font `/Encoding` (or any `/ToUnicode`) is a CMap stream containing attacker-supplied PostScript. veraPDF reuses its CMap parser as a general PostScript interpreter and exposes the unguarded `array N` allocation operator and the `for` control operator with no zero-increment guard. This affects all current versions of veraPDF-parser.

## Details

The vulnerability resides in veraPDF-parser. CMap streams referenced as a Type 0 font's `/Encoding` (or any font's `/ToUnicode`) are parsed by `CMapParser` (veraPDF-parser/src/main/java/org/verapdf/pd/font/cmap/CMapParser.java), which extends `PSParser`. Tokens that are not the small CMap-specific keyword set (`begincodespacerange`, `bfchar`, `cidchar`, ...) fall through to `PSObject.execute` (veraPDF-parser/src/main/java/org/verapdf/parser/postscript/PSObject.java), which dispatches generic PostScript operators implemented in `PSOperator` (veraPDF-parser/src/main/java/org/verapdf/parser/postscript/PSOperator.java).

Two operators in that interpreter take their bound from the PDF and apply no validation:
1. `array` at PSOperator.java:536-547 pops the top number from the operand stack and immediately calls `COSArray.construct(arraySize)`, then loops `arraySize` times appending `COSObject.getEmpty()`. `COSArray.construct(int)` calls `new ArrayList<>(arraySize)` (COSArray.java:102), so the underlying `Object[]` is allocated up-front. Passing `2147483647` (`Integer.MAX_VALUE`) requests a 16 GB backing array on a 64-bit JVM.
2. `for` at PSOperator.java:571-592 reads `initial`, `increment`, and `limit` from the stack and loops `for (long i = initial; i <= limit; i += increment)`. Because `increment` is unchecked, `0 0 1 { } for` produces an infinite-CPU spin (and progressively a heap exhaustion as each iteration pushes `i` onto the operand stack).

`CMapFactory.getCMap` only catches `IOException` and `PostScriptException`; it does not catch `OutOfMemoryError` or wall-clock budget, so the failure propagates out of font model construction and aborts the validation worker.

A single payload byte sequence, the unframed PostScript `2147483647 array`, is sufficient. No `begincmap`/`endcmap` framing is required because the operator runs before the parser ever reaches the CMap structure.

## Impact

This impacts all current releases of the veraPDF-parser. Successful exploitation requires only that the target validate an attacker-supplied PDF; a single Type 0 font with a malicious `/Encoding` (or any `/ToUnicode`) stream is sufficient.

## Proposed Patch

Cap `array` allocation and forbid zero increments in `for`.

As a defensive measure, also wrap `CMapFactory.getCMap` to enforce a wall-clock and operand-stack-size budget on CMap parsing, and audit the remaining unbounded operators (`copy`, `roll`, `dict`) for similar primitives.

## References
- https://github.com/veraPDF/veraPDF-parser/security/advisories/GHSA-jrmc-qg6p-94fp
- https://github.com/veraPDF/veraPDF-parser/pull/703
- https://github.com/veraPDF/veraPDF-parser/commit/73d6ec002b98ce1f3f68640442f8e5d5613c80ce
- https://github.com/veraPDF/veraPDF-parser/commit/cb3538607a549d63504299be1088c85ae48605f4
- https://github.com/veraPDF/veraPDF-parser
