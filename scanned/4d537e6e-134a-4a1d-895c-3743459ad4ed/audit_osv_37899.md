# [M] FOSSBilling has improper SQL neutralization in `Massmailer` recipient filters

## Summary
Severity: Medium
Advisory: CVE-2026-33734
Aliases: GHSA-jf7m-j359-2899
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-33734
Type: osv

## Details
FOSSBilling is a free, open-source billing and client management system. Versions 0.6.0 through 0.7.2 have a SQL injection vulnerability in the `Massmailer` module filter functionality. An authenticated administrator can supply crafted filter values when updating a mass email message, causing untrusted input to be interpolated directly into SQL in the recipient selection query. Version 0.8.0 patches the issue. Some workarounds are available. Restrict administrator access to trusted users only, disable the `Massmailer` module if it is not required, audit existing records in the `mod_massmailer` table for suspicious filter values, and/or review administrator activity related to `Massmailer` message updates.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33734.json
- https://github.com/FOSSBilling/FOSSBilling/security/advisories/GHSA-jf7m-j359-2899
- https://nvd.nist.gov/vuln/detail/CVE-2026-33734
