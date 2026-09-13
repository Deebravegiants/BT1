# [M] Statamic CMS's missing authorization allows access to assets

## Summary
Severity: Medium
Advisory: GHSA-gwmx-9gcj-332h
CVE: CVE-2026-25633
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-11
Source: https://github.com/advisories/GHSA-gwmx-9gcj-332h
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.6
- Packagist: `statamic/cms` — affected >=6.0.0-alpha.1 <6.2.5

## Details
### Impact
Users without permission to view assets are able are able to download them and view their metadata.

Logged-out users and users without permission to access the control panel are unable to take advantage of this.

### Patches
This has been fixed in 5.73.6 and 6.2.5.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-gwmx-9gcj-332h
- https://nvd.nist.gov/vuln/detail/CVE-2026-25633
- https://github.com/statamic/cms/pull/13883
- https://github.com/statamic/cms/commit/5a6f47246edf3a0c453727ffecbfa14333a6bc8a
- https://github.com/statamic/cms
- https://github.com/statamic/cms/releases/tag/v5.73.6
- https://github.com/statamic/cms/releases/tag/v6.2.5
