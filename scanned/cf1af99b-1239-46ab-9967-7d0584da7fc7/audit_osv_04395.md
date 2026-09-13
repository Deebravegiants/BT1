# [M] Multisite denial of service through unsanitized dynamic dispatch to SiteSetting in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-30606
Aliases: CVE-2023-30606, GHSA-jj93-w3mv-3jvv
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-30606
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.1.0

## Details
Discourse is an open source platform for community discussion. In affected versions a user logged as an administrator can call arbitrary methods on the `SiteSetting` class, notably `#clear_cache!` and `#notify_changed!`, which when done on a multisite instance, can affect the entire cluster resulting in a denial of service. Users not running in multisite environments are not affected. This issue is patched in the latest stable, beta and tests-passed versions of Discourse. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-jj93-w3mv-3jvv
- https://nvd.nist.gov/vuln/detail/CVE-2023-30606
