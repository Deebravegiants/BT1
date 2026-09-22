# [M] 2FA bypass through deleting devices in wagtail-2fa

## Summary
Severity: Medium
Advisory: GHSA-9gjv-6qq6-v7qm
CVE: CVE-2020-5240
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2020-03-13
Source: https://github.com/advisories/GHSA-9gjv-6qq6-v7qm
Type: github-advisory

## Affected
- PyPI: `wagtail-2fa` — affected >=0 <1.4.1

## Details
### Impact
Any user with access to the CMS can view and delete other users&#39; 2FA devices by going to the correct path. The user does not require special permissions in order to do so. By deleting the other user&#39;s device they can disable the target user&#39;s 2FA devices and potentially compromise the account if they figure out their password.

### Patches
The problem has been patched in version 1.4.1.

### Workarounds
There is no workaround for this issue.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [github.com/labd/wagtail-2fa](https://github.com/labd/wagtail-2fa)
* Email us at [security@labdigital.nl](mailto:security@labdigital.nl)

## References
- https://github.com/labd/wagtail-2fa/security/advisories/GHSA-9gjv-6qq6-v7qm
- https://nvd.nist.gov/vuln/detail/CVE-2020-5240
- https://github.com/labd/wagtail-2fa/commit/ac23550d33b7436e90e3beea904647907eba5b74
- https://github.com/labd/wagtail-2fa
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail-2fa/PYSEC-2020-219.yaml
