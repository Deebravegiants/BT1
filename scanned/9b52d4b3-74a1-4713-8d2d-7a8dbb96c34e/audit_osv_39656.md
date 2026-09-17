# [M] FlashMQ: Client can trigger uncaught exception on FlashMQ 1.26.1 and older

## Summary
Severity: Medium
Advisory: CVE-2026-46411
Aliases: GHSA-g35r-265r-rxrh
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46411
Type: osv

## Details
FlashMQ is a MQTT broker/server, designed for multi-CPU environments. Prior to version 1.26.2, authorized clients have the ability to exceed the permitted over-commit of their write buffer and triggering an internal safe-guard exception. This exception was in a path that was not catchable, and therefore causes a server abort. This issue has been patched in version 1.26.2.

## References
- https://github.com/halfgaar/FlashMQ/releases/tag/v1.26.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46411.json
- https://github.com/halfgaar/FlashMQ/security/advisories/GHSA-g35r-265r-rxrh
- https://nvd.nist.gov/vuln/detail/CVE-2026-46411
- https://github.com/halfgaar/FlashMQ/commit/29e08f7b97b6e3f96db923c2b6a260c47b49c195
