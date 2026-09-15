# [M] OpenCanary Executes Commands From Potentially Writable Config File

## Summary
Severity: Medium
Advisory: GHSA-pf5v-pqfv-x8jj
CVE: CVE-2024-48911
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-14
Source: https://github.com/advisories/GHSA-pf5v-pqfv-x8jj
Type: github-advisory

## Affected
- PyPI: `OpenCanary` — affected >=0 <0.9.5

## Details
### Impact

OpenCanary directly executed commands taken from its config file. Where the config file is stored in an unprivileged user directory but the daemon is executed by root, it’s possible for the unprivileged user to change the config file and escalate permissions when root later runs the daemon.

Thanks to the folks at [Whirlylabs](https://whirlylabs.com/) for finding and fixing this.

### Patches

Upgrade to 0.9.4 or higher.

## References
- https://github.com/thinkst/opencanary/security/advisories/GHSA-pf5v-pqfv-x8jj
- https://nvd.nist.gov/vuln/detail/CVE-2024-48911
- https://github.com/thinkst/opencanary/commit/2c11575b1a3dd8b0df26a879ba856c0aa350c049
- https://github.com/pypa/advisory-database/tree/main/vulns/opencanary/PYSEC-2024-248.yaml
- https://github.com/thinkst/opencanary
- https://github.com/thinkst/opencanary/releases/tag/v0.9.4
