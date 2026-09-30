# [H] Improper Input Validation in sopel-plugins.channelmgnt

## Summary
Severity: High
Advisory: GHSA-23c7-6444-399m
CVE: CVE-2021-21431
CWE: CWE-20, CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:R/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2021-04-09
Source: https://github.com/advisories/GHSA-23c7-6444-399m
Type: github-advisory

## Affected
- PyPI: `sopel-plugins.channelmgnt` — affected >=0 <2.0.1

## Details
### Impact
On some IRC servers, restrictions around the removal of the bot using the kick/kickban command could be bypassed when kicking multiple users at once.
We also believe it may have been possible to remove users from other channels but due to the wonder that is IRC and following RfCs, We have no POC for that.

Freenode is not affected.

### Patches
Upgrade to 2.0.1 or higher

### Workarounds
Do not use this plugin on networks where TARGMAX > 1.

### For more information
If you have any questions or comments about this advisory:
* Open an issue on [phab](https://phab.mirahezebots.org/maniphest/task/edit/form/1/).
* Email us at [staff(at)mirahezebots(dot)org](mailto:staff@mirahezebots.org)

## References
- https://github.com/MirahezeBots/sopel-channelmgnt/security/advisories/GHSA-23c7-6444-399m
- https://nvd.nist.gov/vuln/detail/CVE-2021-21431
- https://github.com/MirahezeBots/sopel-channelmgnt/commit/643388365f28c5cc682254ab913c401f0e53260a
- https://github.com/MirahezeBots/sopel-channelmgnt/commit/7c96d400358221e59135f0a0be0744f3fad73856
- https://github.com/MirahezeBots/sopel-channelmgnt
- https://github.com/pypa/advisory-database/tree/main/vulns/sopel-plugins-channelmgnt/PYSEC-2021-58.yaml
- https://pypi.org/project/sopel-plugins.channelmgnt
