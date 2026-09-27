# [C] Zerobyte has Authentication Bypass by Primary Weakness

## Summary
Severity: Critical
Advisory: CVE-2025-68435
Aliases: GHSA-x539-c98q-38gv
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-68435
Type: osv

## Details
Zerobyte is a backup automation tool Zerobyte versions prior to 0.18.5 and 0.19.0 contain an authentication bypass vulnerability where authentication middleware is not properly applied to API endpoints. This results in certain API endpoints being accessible without valid session credentials. This is dangerous for those who have exposed Zerobyte to be used outside of their internal network. A fix has been applied in both version 0.19.0 and 0.18.5. If immediate upgrade is not possible, restrict network access to the Zerobyte instance to trusted networks only using firewall rules or network segmentation. This is only a temporary mitigation; upgrading is strongly recommended.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68435.json
- https://github.com/nicotsx/zerobyte/security/advisories/GHSA-x539-c98q-38gv
- https://nvd.nist.gov/vuln/detail/CVE-2025-68435
- https://github.com/nicotsx/zerobyte/issues/161
- https://github.com/nicotsx/zerobyte/commit/13e080a18967705bd2b4e110e5f7693fdca1c692
