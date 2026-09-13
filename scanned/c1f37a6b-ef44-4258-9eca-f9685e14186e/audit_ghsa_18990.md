# [H] Valibot has a ReDoS vulnerability in `EMOJI_REGEX`

## Summary
Severity: High
Advisory: GHSA-vqpr-j7v3-hqw9
CVE: CVE-2025-66020
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-26
Source: https://github.com/advisories/GHSA-vqpr-j7v3-hqw9
Type: github-advisory

## Affected
- npm: `valibot` — affected >=0.31.0 <1.2.0

## Details
### Summary

The `EMOJI_REGEX` used in the `emoji` action is vulnerable to a Regular Expression Denial of Service (ReDoS) attack. A short, maliciously crafted string (e.g., <100 characters) can cause the regex engine to consume excessive CPU time (minutes), leading to a Denial of Service (DoS) for the application.

### Details

The ReDoS vulnerability stems from "catastrophic backtracking" in the `EMOJI_REGEX`. This is caused by ambiguity in the regex pattern due to overlapping character classes.

Specifically, the class `\p{Emoji_Presentation}` overlaps with more specific classes used in the same alternation, such as `[\u{1F1E6}-\u{1F1FF}]` (regional indicator symbols used for flags) and `\p{Emoji_Modifier_Base}`.

When the regex engine attempts to match a string that almost matches but ultimately fails (like the one in the PoC), this ambiguity forces it to explore an exponential number of possible paths. The matching time increases exponentially with the length of the crafted input, rather than linearly.

### PoC

The following code demonstrates the vulnerability.

```javascript
import * as v from 'valibot';

const schema = v.object({
  x: v.pipe(v.string(), v.emoji()),
});

const attackString = '\u{1F1E6}'.repeat(49) + '0';

console.log(`Input length: ${attackString.length}`);
console.log('Starting parse... (This will take a long time)');

// On my machine, a length of 99 takes approximately 2 minutes.
console.time();
try {
  v.parse(schema, {x: attackString });
} catch (e) {}
console.timeEnd();
```

### Impact

Any project using Valibot's `emoji` validation on user-controllable input is vulnerable to a Denial of Service attack.

An attacker can block server resources (e.g., a web server's event loop) by submitting a short string to any endpoint that uses this validation. This is particularly dangerous because the attack string is short enough to bypass typical input length restrictions (e.g., maxLength(100)).

### Recommended Fix

The root cause is the overlapping character classes. This can be resolved by making the alternatives mutually exclusive, typically by using negative lookaheads (`(?!...)`) to subtract the specific classes from the more general one.

The following modified `EMOJI_REGEX` applies this principle:

```javascript
export const EMOJI_REGEX: RegExp =
  // eslint-disable-next-line redos-detector/no-unsafe-regex, regexp/no-dupe-disjunctions -- false positives
  /^(?:[\u{1F1E6}-\u{1F1FF}]{2}|\u{1F3F4}[\u{E0061}-\u{E007A}]{2}[\u{E0030}-\u{E0039}\u{E0061}-\u{E007A}]{1,3}\u{E007F}|(?:\p{Emoji}\uFE0F\u20E3?|\p{Emoji_Modifier_Base}\p{Emoji_Modifier}?|(?![\p{Emoji_Modifier_Base}\u{1F1E6}-\u{1F1FF}])\p{Emoji_Presentation})(?:\u200D(?:\p{Emoji}\uFE0F\u20E3?|\p{Emoji_Modifier_Base}\p{Emoji_Modifier}?|(?![\p{Emoji_Modifier_Base}\u{1F1E6}-\u{1F1FF}])\p{Emoji_Presentation}))*)+$/u;
```

## References
- https://github.com/open-circle/valibot/security/advisories/GHSA-vqpr-j7v3-hqw9
- https://nvd.nist.gov/vuln/detail/CVE-2025-66020
- https://github.com/open-circle/valibot/commit/cfb799db301a953a0950d5c05a34a3ab121262dc
- https://github.com/open-circle/valibot
