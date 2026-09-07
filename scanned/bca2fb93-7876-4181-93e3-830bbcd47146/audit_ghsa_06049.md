# [H] docx4j: Stack Overflow via Cyclic `w:basedOn` Style Chain leads to Denial of Service

## Summary
Severity: High
Advisory: GHSA-gc95-3vw8-vg43
CVE: CVE-2026-53752
CWE: CWE-674, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-gc95-3vw8-vg43
Type: github-advisory

## Affected
- Maven: `org.docx4j:docx4j-core` — affected >=0 <11.5.14

## Details
### Summary
docx4j's `PropertyResolver` and several adjacent helpers recursively walk the OpenXML style inheritance chain (`w:basedOn`) without cycle detection. 

A WordprocessingML document containing a cyclic style chain (for example, Style A based on B and Style B based on A) causes unbounded recursion and a `java.lang.StackOverflowError` within the property-resolution code path.

These helpers are used by operations that require effective style resolution, including common conversion and TOC-related paths.  As a result, most server-side pipelines that accept a user-supplied docx and process it through docx4j can likely be crashed by a file containing a cyclic style reference.

### Details

Representative snippet: `PropertyResolver.fillPPrStack`

```java
private void fillPPrStack(String styleId, Stack<PPr> pPrStack) {
    Style style = liveStyles.get(styleId);
    ...
    // if it is based on, recurse
    if (style.getBasedOn() == null) {
        log.debug("Style " + styleId + " is a root style.");
    } else if (style.getBasedOn().getVal() != null) {
        String basedOnStyleName = style.getBasedOn().getVal();
        fillPPrStack(basedOnStyleName, pPrStack);   // ← unbounded recursion
        ...
```

### Impact
This is a denial of service against a server-side application that processes untrusted docx files via docx4j. 

An upload causes the processing thread to be terminated with `StackOverflowError` which may crash the worker thread, degrade the thread pool, or evade normal per-request CPU and heap-memory safeguards in containers and serverless functions (because the failure mode is thread-stack exhaustion rather than gradual resource consumption).

The attack depends on the host application's access controls and requires no user interaction beyond submitting the file. Detection is difficult because the file is a well-formed OOXML package containing ordinary style elements,  and passes standard antivirus and content-inspection rules.

Severity: High for server-side applications that process untrusted DOCX files using docx4j style/property resolution (unless the application catches StackOverflowError, isolates conversion in disposable worker processes, restarts workers cleanly, and the practical impact is only failure of one request). Severity may be Medium where document upload requires authentication, processing is isolated, or the failure is limited to a single request/worker.

### Credits
Thanks to Koh You Liang ([@Isopach](https://github.com/Isopach)) for responsibly disclosing this issue.

## References
- https://github.com/plutext/docx4j/security/advisories/GHSA-gc95-3vw8-vg43
- https://github.com/plutext/docx4j
- https://github.com/plutext/docx4j/releases/tag/docx4j-11.5.14
