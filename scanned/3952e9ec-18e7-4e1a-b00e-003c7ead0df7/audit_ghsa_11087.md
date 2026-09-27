# [C] Graphiti Affected by Arbitrary Method Execution via Unvalidated Relationship Names

## Summary
Severity: Critical
Advisory: GHSA-3m5v-4xp5-gjg2
CVE: CVE-2026-33286
CWE: CWE-913
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-3m5v-4xp5-gjg2
Type: github-advisory

## Affected
- RubyGems: `graphiti` — affected >=0 <1.10.2

## Details
### Summary

An arbitrary method execution vulnerability has been found which affects Graphiti's JSONAPI write functionality. An attacker can craft a malicious JSONAPI payload with arbitrary relationship names to invoke any public method on the underlying model instance, class or its associations.

### Impact

Any application exposing Graphiti write endpoints (create/update/delete) to untrusted users is affected. 

The `Graphiti::Util::ValidationResponse#all_valid?` method recursively calls `model.send(name)` using relationship names taken directly from user-supplied JSONAPI payloads, without validating them against the resource's configured sideloads. This allows an attacker to potentially run any public method on a given model instance, on the instance class or associated instances or classes, including destructive operations.

### Patches

This is patched in Graphiti **v1.10.2**. Users should upgrade as soon as possible.

### Workarounds

If upgrading to v1.10.2 is not immediately possible, consider one or more of the following mitigations:

- **Restrict write access**: Ensure Graphiti write endpoints (create/update/delete) are not accessible to untrusted users.
- **Authentication & authorisation**: Apply strong authentication and authorisation checks before any write operation is processed, for example use Rails strong parameters to ensure only valid parameters are processed.

## References
- https://github.com/graphiti-api/graphiti/security/advisories/GHSA-3m5v-4xp5-gjg2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33286
- https://github.com/graphiti-api/graphiti/commit/ddb5ad2b69330774bd1a47935ed89a9fe4396a54
- https://github.com/graphiti-api/graphiti
- https://github.com/graphiti-api/graphiti/releases/tag/v1.10.2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/graphiti/CVE-2026-33286.yml
