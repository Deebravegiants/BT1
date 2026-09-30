# [M] Ash.update_many/4 atomic path skips resource policy authorization, allowing updates to forbidden records

## Summary
Severity: Medium
Advisory: CVE-2026-82746
Aliases: EEF-CVE-2026-82746, GHSA-j7c9-3fw3-jc64
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-82746
Type: osv

## Details
Missing Authorization vulnerability in ash-project ash allows an actor to update records forbidden by resource policies through the atomic path of Ash.update_many/4.

Ash.update_many/4 runs as a single atomic statement (a data-layer update_many, for example a SQL MERGE) whenever an atomic strategy is used and the data layer supports it. Ash.Actions.Update.UpdateMany (lib/ash/actions/update/update_many.ex) took that path even under authorize?: true without applying the resource's policies, so the statement updated every row matched by primary key regardless of the policy filter that authorization would impose. An actor could therefore update records the policies forbid, such as rows belonging to another actor or tenant. The fix restricts the atomic path to data layers supporting changeset filters when authorizing, authorizes each changeset, and merges the resulting policy filter into each changeset so the statement only touches authorized rows.

This issue affects ash: from 3.29.0 before 3.32.2.

## References
- https://cna.erlef.org/cves/CVE-2026-82746.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82746
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82746.json
- https://github.com/ash-project/ash/security/advisories/GHSA-j7c9-3fw3-jc64
- https://nvd.nist.gov/vuln/detail/CVE-2026-82746
- https://github.com/ash-project/ash/commit/ed4e656822ffe83f8e960d5de0b573c0d1ae7f29
- https://github.com/ash-project/ash
