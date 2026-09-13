# [M] Privilege Escalation in Channelmgnt plug-in for Sopel

## Summary
Severity: Medium
Advisory: GHSA-j257-jfvv-h3x5
CVE: CVE-2020-15251
CWE: CWE-862, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-10-13
Source: https://github.com/advisories/GHSA-j257-jfvv-h3x5
Type: github-advisory

## Affected
- PyPI: `sopel_plugins.channelmgnt` — affected >=0 <1.0.3
- PyPI: `sopel-plugins-channelmgnt` — affected >=0 <1.0.3

## Details
### Impact
Malicious users are able to op/voice and take over a channel

### Patches
On version 1.0.3

### Workarounds
Disable channelmgnt

### References
https://phab.bots.miraheze.wiki/T117

### For more information
If you have any questions or comments about this advisory:
* Email us at [staff(at)mirahezebots(dot)org](mailto:staff@mirahezebots.org)

## References
- https://github.com/MirahezeBots/MirahezeBots/security/advisories/GHSA-23pc-4339-95vg
- https://github.com/MirahezeBots/sopel-channelmgnt/security/advisories/GHSA-j257-jfvv-h3x5
- https://nvd.nist.gov/vuln/detail/CVE-2020-15251
- https://github.com/MirahezeBots/sopel-channelmgnt/pull/3
- https://github.com/MirahezeBots/MirahezeBots
- https://github.com/pypa/advisory-database/tree/main/vulns/sopel-plugins-channelmgnt/PYSEC-2020-110.yaml
- https://phab.bots.miraheze.wiki/T117
- https://phab.bots.miraheze.wiki/phame/live/1/post/1/summary
- https://pypi.org/project/sopel-plugins.channelmgnt
