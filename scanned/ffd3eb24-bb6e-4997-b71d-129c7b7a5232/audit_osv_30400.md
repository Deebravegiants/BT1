# [C] Tolgee's configuration all configuration properties leaked in public configuration DTO

## Summary
Severity: Critical
Advisory: CVE-2024-52297
Aliases: GHSA-3wr3-889v-pgcj
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-12
Source: https://osv.dev/vulnerability/CVE-2024-52297
Type: osv

## Details
Tolgee is an open-source localization platform. Tolgee 3.81.1 included the all configuration properties in the PublicConfiguratioDTO publicly exposed to users. This vulnerability is fixed in v3.81.2.

## References
- https://github.com/tolgee/tolgee-platform/pull/2481/files#diff-d16735590f0f2db7cd782e2966fa18426b94b5e4030fa8b1f5e00cd55686fe7f
- https://github.com/tolgee/tolgee-platform/pull/2689/files
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52297.json
- https://github.com/tolgee/tolgee-platform/security/advisories/GHSA-3wr3-889v-pgcj
- https://nvd.nist.gov/vuln/detail/CVE-2024-52297
