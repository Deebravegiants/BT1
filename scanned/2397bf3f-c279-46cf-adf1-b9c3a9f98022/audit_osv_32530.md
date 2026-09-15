# [M] Finit has heap based buffer overwrite in urandom.so plugin

## Summary
Severity: Medium
Advisory: CVE-2025-32022
Aliases: GHSA-fv6v-vw8h-9x79
CVSS: 4.6 (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:N/I:H/A:L)
Published: 2025-05-06
Source: https://osv.dev/vulnerability/CVE-2025-32022
Type: osv

## Details
Finit provides fast init for Linux systems. Finit's urandom plugin has a heap buffer overwrite vulnerability at boot which leads to it overwriting other parts of the heap, possibly causing random instabilities and undefined behavior. The urandom plugin is enabled by default, so this bug affects everyone using Finit 4.2 or later that do not explicitly disable the plugin at build time. This bug is fixed in Finit 4.12. Those who cannot upgrade or backport the fix to urandom.c are strongly recommended to disable the plugin in the call to the `configure` script.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32022.json
- https://github.com/troglobit/finit/security/advisories/GHSA-fv6v-vw8h-9x79
- https://nvd.nist.gov/vuln/detail/CVE-2025-32022
- https://github.com/troglobit/finit/commit/3feff37ba51fa0a6a0a06f59682a0918aa5b04de
