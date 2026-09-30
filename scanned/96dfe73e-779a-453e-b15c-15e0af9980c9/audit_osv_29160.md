# [M] Implicit override for built-in materializations from installed packages in dbt-core

## Summary
Severity: Medium
Advisory: CVE-2024-40637
Aliases: GHSA-p3f3-5ccg-83xq, PYSEC-2024-66
CVSS: 4.2 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2024-40637
Type: osv

## Details
dbt enables data analysts and engineers to transform their data using the same practices that software engineers use to build applications. When a user installs a package in dbt, it has the ability to override macros, materializations, and other core components of dbt. This is by design, as it allows packages to extend and customize dbt's functionality. However, this also means that a malicious package could potentially override these components with harmful code. This issue has been fixed in versions 1.8.0, 1.6.14 and 1.7.14. Users are advised to upgrade. There are no kn own workarounds for this vulnerability. Users updating to either 1.6.14 or 1.7.14 will need to set `flags.require_explicit_package_overrides_for_builtin_materializations: False` in their configuration in `dbt_project.yml`.

## References
- https://docs.getdbt.com/docs/build/packages
- https://docs.getdbt.com/reference/global-configs/legacy-behaviors#behavior-change-flags
- https://tempered.works/posts/2024/07/06/preventing-data-theft-with-gcp-service-controls
- https://www.elementary-data.com/post/are-dbt-packages-secure-the-answer-lies-in-your-dwh-policies
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40637.json
- https://github.com/dbt-labs/dbt-core/security/advisories/GHSA-p3f3-5ccg-83xq
- https://nvd.nist.gov/vuln/detail/CVE-2024-40637
- https://github.com/dbt-labs/dbt-core/commit/3c82a0296d227cb1be295356df314c11716f4ff6
- https://github.com/dbt-labs/dbt-core/commit/87ac4deb00cc9fe334706e42a365903a1d581624
- https://www.equalexperts.com/blog/tech-focus/are-you-at-risk-from-this-critical-dbt-vulnerability
