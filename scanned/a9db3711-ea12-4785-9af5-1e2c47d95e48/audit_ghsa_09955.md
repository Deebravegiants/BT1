# [M] Emissary has a Path Traversal via Blacklist Bypass in Configuration API

## Summary
Severity: Medium
Advisory: GHSA-hxf2-gm22-7vcm
CVE: CVE-2026-35583
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-hxf2-gm22-7vcm
Type: github-advisory

## Affected
- Maven: `gov.nsa.emissary:emissary` — affected >=0 <8.39.0

## Details
## Summary

The configuration API endpoint (`/api/configuration/{name}`) validated
configuration names using a blacklist approach that checked for `\`, `/`, `..`,
and trailing `.`. This could potentially be bypassed using URL-encoded variants,
double-encoding, or Unicode normalization to achieve path traversal and read
configuration files outside the intended directory.

## Details

### Vulnerable code — `Configs.java` (line 126)

```java
protected static String validate(String config) {
    if (StringUtils.isBlank(config) || config.contains("\\") || config.contains("/")
        || config.contains("..") || config.endsWith(".")) {
        throw new IllegalArgumentException("Invalid config name: " + config);
    }
    return Strings.CS.appendIfMissing(config.trim(), CONFIG_FILE_ENDING);
}
```

### Weakness

The blacklist blocked literal `\`, `/`, `..`, and trailing `.` but could
potentially miss:

- URL-encoded variants (`%2e%2e%2f`) if decoded after validation
- Double-encoded sequences (`%252e%252e%252f`)
- Unicode normalization bypasses
- The approach relies on string matching rather than canonical path resolution

### Impact

- Potential read access to configuration files outside the intended config
  directory
- Information disclosure of sensitive configuration values

## Remediation

Fixed in [PR #1292](https://github.com/NationalSecurityAgency/emissary/pull/1292),
merged into release 8.39.0.

The blacklist was replaced with an allowlist regex that only permits characters
matching `^[a-zA-Z0-9._-]+$`:

```java
protected static final Pattern VALID_CONFIG_NAME = Pattern.compile("^[a-zA-Z0-9._-]+$");

protected static String validate(String config) {
    if (!VALID_CONFIG_NAME.matcher(config).matches() || config.contains("..") || config.endsWith(".")) {
        throw new IllegalArgumentException("Invalid config name: " + config);
    }
    return Strings.CS.appendIfMissing(config.trim(), CONFIG_FILE_ENDING);
}
```

This ensures that any character outside the allowed set — including encoded
slashes, percent signs, and Unicode sequences — is rejected before the config
name reaches the filesystem.

Tests were added to verify that URL-encoded (`%2e%2e%2f`), double-encoded
(`%252e%252e%252f`), and Unicode (`U+002F`) traversal attempts are blocked.

## Workarounds

If upgrading is not immediately possible, deploy a reverse proxy or WAF rule
that rejects requests to `/api/configuration/` containing encoded path traversal
sequences.

## References

- [PR #1292 — validate config name with an allowlist](https://github.com/NationalSecurityAgency/emissary/pull/1292)
- Original report: GHSA-wjqm-p579-x3ww

## References
- https://github.com/NationalSecurityAgency/emissary/security/advisories/GHSA-hxf2-gm22-7vcm
- https://nvd.nist.gov/vuln/detail/CVE-2026-35583
- https://github.com/NationalSecurityAgency/emissary/pull/1292
- https://github.com/NationalSecurityAgency/emissary
