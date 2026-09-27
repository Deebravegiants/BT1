# [M] Job argument injection via :args overrides primary_key and tenant in AshOban

## Summary
Severity: Medium
Advisory: CVE-2026-78038
Aliases: EEF-CVE-2026-78038, GHSA-gj9p-x393-rf9h
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-78038
Type: osv

## Details
Improperly Controlled Modification of Dynamically-Determined Object Attributes vulnerability in ash-project ash_oban allows a user whose input reaches the :args option of AshOban.build_trigger/3 to retarget an update or destroy trigger at another record, including across tenants.

build_trigger/3 builds the trusted job arguments with atom keys (:primary_key, :tenant, :action_arguments) and merges the caller's :args underneath so the trusted values win on collision. Because Oban job arguments round-trip through JSON, the caller's keys arrive as strings, so Map.merge sees no collision and both keys survive. When the job is persisted the JSON object is de-duplicated keeping the last (string) key, and the worker reads the caller's value. The documentation describes :args as unable to affect the action, so an application that forwards user input into it for uniqueness scoping is exposed to authorization bypass and tenant isolation breaks.

This issue affects ash_oban: from 0.2.5 before 0.8.14.

## References
- https://cna.erlef.org/cves/CVE-2026-78038.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-78038
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78038.json
- https://github.com/ash-project/ash_oban/security/advisories/GHSA-gj9p-x393-rf9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-78038
- https://github.com/ash-project/ash_oban/commit/da2d81e1e8e1dcc3e6ec8587cdb4f273575ffca3
- https://github.com/ash-project/ash_oban
