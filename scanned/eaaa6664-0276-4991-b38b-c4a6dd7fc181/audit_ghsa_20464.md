# [H] october/system arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-5hfj-r725-wpc4
CVE: CVE-2021-32650
CWE: CWE-74, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-14
Source: https://github.com/advisories/GHSA-5hfj-r725-wpc4
Type: github-advisory

## Affected
- Packagist: `october/system` — affected >=1.1.0 <1.1.6
- Packagist: `october/system` — affected >=0 <1.0.473

## Details
### Impact

Assuming an attacker with access to the backend is able to execute PHP code by using the theme import feature. This will bypass the safe mode feature that prevents PHP execution in the CMS templates.

### Patches

Issue has been patched in Build 473 and v1.1.6

### Workarounds

Apply https://github.com/octobercms/october/commit/167b592eed291ae1563c8fcc5b9b34a03a300f26 to your installation manually if you are unable to upgrade.

### References

Credits to:
• Sushi Yushi

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

## References
- https://github.com/octobercms/october/security/advisories/GHSA-5hfj-r725-wpc4
- https://nvd.nist.gov/vuln/detail/CVE-2021-32650
- https://github.com/octobercms/october/commit/167b592eed291ae1563c8fcc5b9b34a03a300f26
- https://github.com/octobercms/october
