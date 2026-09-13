# [H] Faraday: Uncontrolled recursion in NestedParamsEncoder allows stack exhaustion DoS via deeply nested query parameters

## Summary
Severity: High
Advisory: GHSA-98m9-hrrm-r99r
CVE: CVE-2026-54297
CWE: CWE-674
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-98m9-hrrm-r99r
Type: github-advisory

## Affected
- RubyGems: `faraday` — affected >=2.0.0 <2.14.3
- RubyGems: `faraday` — affected >=1.0.0 <1.10.6

## Details
`Faraday::NestedParamsEncoder`, the default nested query parameter encoder/decoder in Faraday, decodes nested query strings without enforcing a maximum nesting depth.

A crafted query string such as:

```text
a[x][x][x][x]...[x]=1
```

causes Faraday to build a deeply nested Ruby `Hash` structure. The internal `dehash` routine then recursively walks this attacker-controlled structure without a depth limit. At sufficient depth, Ruby raises an uncaught `SystemStackError` (`stack level too deep`), crashing the calling thread or worker. This can lead to denial of service in applications that pass attacker-controlled query strings to Faraday's nested query parsing or URL-building paths.

This has been patched in version 2.14.3 and backported to 1.10.6.

## References
- https://github.com/lostisland/faraday/security/advisories/GHSA-98m9-hrrm-r99r
- https://nvd.nist.gov/vuln/detail/CVE-2026-54297
- https://github.com/lostisland/faraday/pull/1681
- https://github.com/lostisland/faraday
- https://github.com/lostisland/faraday/releases/tag/v1.10.6
- https://github.com/lostisland/faraday/releases/tag/v2.14.3
