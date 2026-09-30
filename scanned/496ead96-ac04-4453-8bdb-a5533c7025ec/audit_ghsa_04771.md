# [H] Muhammara has a NULL pointer dereference in LZWDecode filter when DecodeParms omits EarlyChange key

## Summary
Severity: High
Advisory: GHSA-fhp4-pr5j-46m5
CWE: CWE-476
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-fhp4-pr5j-46m5
Type: github-advisory

## Affected
- npm: `muhammara` — affected >=0 <6.0.5

## Details
## Summary

A NULL pointer dereference vulnerability exists in `PDFParser::CreateFilterForStream()` when processing a PDF stream with `/Filter /LZWDecode` and a `/DecodeParms` dictionary that does not contain the `EarlyChange` key. This causes an access violation (0xC0000005) and crashes the process.

## Affected Version

muhammara <= 6.0.4 (latest)

## Vulnerability Details

**File:** `src/deps/PDFWriter/PDFParser.cpp` line 2107

```cpp
if (inDecodeParams)
{
    PDFObjectCastPtr<PDFInteger> earlyObj(
        QueryDictionaryObject(inDecodeParams, "EarlyChange")
    );
    early = earlyObj->GetValue();  // NULL dereference when EarlyChange key is absent
}
```

When `inDecodeParams` is non-NULL but lacks the `EarlyChange` key:
1. `QueryDictionaryObject()` returns NULL
2. `PDFObjectCastPtr<PDFInteger>(NULL)` wraps NULL
3. `earlyObj->GetValue()` dereferences NULL → crash

## PoC

460-byte malicious PDF triggers crash via `startReadingFromStream()`:

- PDF contains `/Filter /LZWDecode` with `/DecodeParms << >>` (empty, no EarlyChange)
- Exit code: `0xC0000005` (Access Violation)

## Fix

```cpp
if (earlyObj)
    early = earlyObj->GetValue();
```

## Impact

Any application accepting untrusted PDFs and using muhammara to read stream contents is vulnerable to DoS.

Similar to: CVE-2022-41957, CVE-2022-39381

## PoC File
[poc_muhammara_lzw_null.js](https://github.com/user-attachments/files/27186113/poc_muhammara_lzw_null.js)

## References
- https://github.com/julianhille/MuhammaraJS/security/advisories/GHSA-fhp4-pr5j-46m5
- https://github.com/julianhille/MuhammaraJS/commit/a98c07780241353334eb65bfca1df025f14be70b
- https://github.com/julianhille/MuhammaraJS
