# [M] 2FA bypass in Wagtail through new device path

## Summary
Severity: Medium
Advisory: GHSA-89px-ww3j-g2mm
CVE: CVE-2019-16766
CWE: CWE-290, CWE-304
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2019-11-29
Source: https://github.com/advisories/GHSA-89px-ww3j-g2mm
Type: github-advisory

## Affected
- PyPI: `wagtail-2fa` — affected >=0 <1.3.0

## Details
## 2FA bypass through new device path

### Impact
If someone gains access to someone's Wagtail login credentials, they can log into the CMS and bypass the 2FA check by changing the URL. They can then add a new device and gain full access to the CMS.

### Patches
This problem has been patched in version 1.3.0.

### Workarounds
There is no workaround at the moment.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [github.com/labd/wagtail-2fa](https://github.com/labd/wagtail-2fa)
* Email us at [security@labdigital.nl](mailto:security@labdigital.nl)

## References
- https://github.com/labd/wagtail-2fa/security/advisories/GHSA-89px-ww3j-g2mm
- https://nvd.nist.gov/vuln/detail/CVE-2019-16766
- https://github.com/labd/wagtail-2fa/commit/13b12995d35b566df08a17257a23863ab6efb0ca
- https://github.com/labd/wagtail-2fa/commit/a6711b29711729005770ff481b22675b35ff5c81
- https://github.com/labd/wagtail-2fa
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail-2fa/PYSEC-2019-135.yaml
