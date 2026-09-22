# [M] path-to-regexp vulnerable to Regular Expression Denial of Service via multiple wildcards

## Summary
Severity: Medium
Advisory: GHSA-27v5-c462-wpq7
CVE: CVE-2026-4923
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-27v5-c462-wpq7
Type: github-advisory

## Affected
- npm: `path-to-regexp` — affected >=8.0.0 <8.4.0

## Details
### Impact

When using multiple wildcards, combined with at least one parameter, a regular expression can be generated that is vulnerable to ReDoS. This backtracking vulnerability requires the second wildcard to be somewhere other than the end of the path.

**Unsafe examples:**

```
/*foo-*bar-:baz
/*a-:b-*c-:d
/x/*a-:b/*c/y
```

**Safe examples:**

```
/*foo-:bar
/*foo-:bar-*baz
```

### Patches

Upgrade to version `8.4.0`.

### Workarounds

If developers are using multiple wildcard parameters, they can check the regex output with a tool such as https://makenowjust-labs.github.io/recheck/playground/ to confirm whether a path is vulnerable.

## References
- https://github.com/pillarjs/path-to-regexp/security/advisories/GHSA-27v5-c462-wpq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-4923
- https://cna.openjsf.org/security-advisories.html
- https://github.com/pillarjs/path-to-regexp
- https://makenowjust-labs.github.io/recheck/playground
