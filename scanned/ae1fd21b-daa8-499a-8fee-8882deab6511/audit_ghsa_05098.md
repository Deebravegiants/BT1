# [M] Bugsink: Project scoping missing in sourcemap and debug-file lookup

## Summary
Severity: Medium
Advisory: GHSA-5389-f7vh-wxj8
CVE: CVE-2026-47728
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-5389-f7vh-wxj8
Type: github-advisory

## Affected
- PyPI: `bugsink` — affected >=0 <2.2.0

## Details
### Summary

Bugsink before 2.2.0 resolved sourcemaps and debug files by debug ID without scoping that lookup to the project that owned the uploaded metadata. An authenticated user with access to one project could cause event processing in that project to use sourcemap/debug-file metadata uploaded for another project in the same Bugsink instance, if the same debug ID was referenced.

### Impact

This could disclose source context or symbolication-derived context from another project on the same Bugsink instance.

For sourcemaps, the documented upload flow used `sentry-cli sourcemaps upload` with `--project=ignoredfornow`. In other words, Bugsink did not historically treat the project value supplied during sourcemap upload as meaningful project ownership. This was documented, but at the same time the `sentry-cli`, which requires project as a parameter, was the recommended mechanism for uploads. This could reasonably lead people to expect that sourcemaps uploads would respect the provided project-boundary.

For minidumps/debug files specifically, the affected functionality also required `FEATURE_MINIDUMPS` to be enabled. That feature was marked experimental.

The practical impact is further limited by Bugsink’s deployment model: self-hosted instances are commonly operated within a single organization/trust domain, and Hosted Bugsink uses separate Bugsink instances per tenant. The issue does not cross Hosted Bugsink tenant boundaries.

### Affected Versions
2.1.3 and earlier are affected.

### Patched Versions
2.2.0 fixes this issue.

### Post-Upgrade Notes

After upgrading, upload sourcemaps/debug files with project information.

To remove legacy projectless sourcemap metadata immediately, run, after upgrading:

```
bugsink-manage delete_legacy_sourcemaps
```

## References
- https://github.com/bugsink/bugsink/security/advisories/GHSA-5389-f7vh-wxj8
- https://nvd.nist.gov/vuln/detail/CVE-2026-47728
- https://github.com/bugsink/bugsink
- https://github.com/bugsink/bugsink/releases/tag/2.2.0
