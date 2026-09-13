# [H] @logtape/syslog: syslog log injection via unescaped control characters and unvalidated SD-NAME keys

## Summary
Severity: High
Advisory: GHSA-8h6h-x5pq-56fq
CVE: CVE-2026-54511
CWE: CWE-117, CWE-93
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-8h6h-x5pq-56fq
Type: github-advisory

## Affected
- npm: `@logtape/syslog` — affected >=2.1.0 <2.1.5
- npm: `@logtape/syslog` — affected >=2.0.0 <2.0.14
- npm: `@logtape/syslog` — affected >=0 <1.3.11

## Details
`@logtape/syslog` contains two related output-encoding bugs in the structured data formatting code. Both only affect deployments with `includeStructuredData: true`, which is non-default.

## 1. Unescaped C0 control characters in structured data values

`escapeStructuredDataValue()` in `packages/syslog/src/syslog.ts` escapes `\`, `"`, and `]` per RFC 5424 but does not escape newline (`\n`), carriage return (`\r`), or any other C0 control characters (U+0000–U+001F):

```typescript
function escapeStructuredDataValue(value: string): string {
  return value
    .replace(/\\/g, "\\\\")
    .replace(/"/g, '\\"')
    .replace(/]/g, "\\]");
  // \n, \r, and other C0 control characters are not escaped
}
```

TCP syslog commonly uses `\n` as a frame delimiter (RFC 6587, non-transparent framing). If an attacker-controlled value contains a literal newline, that newline terminates the current syslog frame. Bytes following the newline begin a new frame, and if they form a valid RFC 5424 header (`<PRI>1 …`), a downstream collector will accept them as a separate, authentic-looking syslog record.

## 2. Unvalidated SD-NAME keys

Structured data parameter keys are inserted into the message without validation or escaping:

```typescript
elements.push(`${key}="${escapedValue}"`);
```

RFC 5424 defines SD-NAME as printable US-ASCII characters excluding `=`, `]`, `"`, and space, with a maximum length of 32. A key containing any of those characters, control characters, or exceeding the length limit will produce malformed structured data. If the key itself contains an embedded `]`, it can prematurely close the structured-data element.

In typical usage, property keys are developer-defined string literals and therefore safe. However, if an application forwards attacker-controlled keys as log properties—for example by spreading request headers or arbitrary metadata into a log record—this becomes a second injection path.

## Proof of concept

The following Node.js snippet (no dependencies, no network required) demonstrates that the escaped value still contains a literal newline:

```javascript
function escapeStructuredDataValue(value) {
  return value
    .replace(/\\/g, "\\\\")
    .replace(/"/g, '\\"')
    .replace(/]/g, "\\]");
}

const payload =
  'normal\n<134>1 2026-01-01T00:00:00Z forged evil - - - INJECTED';

const result = escapeStructuredDataValue(payload);
console.log("Newline present after escape:", result.includes("\n")); // true
```

Tested with Node.js 22.17.1.

## Impact

An attacker who controls log property values can:

- forge syslog records attributed to arbitrary hosts, applications, or process IDs;
- insert records with arbitrary severity or facility levels;
- obscure malicious activity by injecting misleading entries around legitimate ones;
- break downstream log parsers or SIEM correlation rules that rely on log integrity.

Affected downstream collectors include rsyslog, syslog-ng, Splunk, Elastic Stack, and any other system using RFC 6587 non-transparent framing.

## Suggested fix

### Structured data values

Escape all C0 control characters (U+0000–U+001F) in addition to `\`, `"`, and `]`. RFC 5424 does not define an escape sequence for control characters in PARAM-VALUE; the most interoperable approach is to strip or replace them:

```typescript
function escapeStructuredDataValue(value: string): string {
  return value
    .replace(/\\/g, "\\\\")
    .replace(/"/g, '\\"')
    .replace(/]/g, "\\]")
    .replace(/[\x00-\x1f]/g, (c) =>
      `\\x${c.charCodeAt(0).toString(16).padStart(2, "0")}`
    );
}
```

Alternatively, strip them entirely: `.replace(/[\x00-\x1f]/g, "")`. The right choice depends on whether downstream consumers need some representation of the original value.

### SD-NAME keys

Validate each key against the RFC 5424 SD-NAME grammar before including it. Keys that fail validation should be skipped or sanitized:

```typescript
// SD-NAME: printable US-ASCII, excluding '=', ']', '"', SP; max 32 chars
const SD_NAME_RE = /^[!-<>-Z\\^-z|~]{1,32}$/;

for (const [key, value] of Object.entries(record.properties)) {
  if (!SD_NAME_RE.test(key)) continue;
  const escapedValue = escapeStructuredDataValue(String(value));
  elements.push(`${key}="${escapedValue}"`);
}
```

## References
- https://github.com/dahlia/logtape/security/advisories/GHSA-8h6h-x5pq-56fq
- https://github.com/dahlia/logtape/commit/7a6e5b9ddf7915edfff78fa129bc17c979b2a623
- https://github.com/dahlia/logtape
- https://github.com/dahlia/logtape/releases/tag/1.3.11
- https://github.com/dahlia/logtape/releases/tag/2.0.14
- https://github.com/dahlia/logtape/releases/tag/2.1.5
