# [H] jquery-validation ReDoS in url2 due to incomplete fix of CVE-2021-43306

## Summary
Severity: High
Advisory: CVE-2022-31147
Aliases: GHSA-ffmh-x56j-9rc3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-07-14
Source: https://osv.dev/vulnerability/CVE-2022-31147
Type: osv

## Details
The jQuery Validation Plugin (jquery-validation) provides drop-in validation for forms. Versions of jquery-validation prior to 1.19.5 are vulnerable to regular expression denial of service (ReDoS) when an attacker is able to supply arbitrary input to the url2 method. This is due to an incomplete fix for CVE-2021-43306. Users should upgrade to version 1.19.5 to receive a patch.

## References
- https://github.com/jquery-validation/jquery-validation/releases/tag/1.19.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31147.json
- https://github.com/jquery-validation/jquery-validation/security/advisories/GHSA-ffmh-x56j-9rc3
- https://nvd.nist.gov/vuln/detail/CVE-2022-31147
- https://github.com/jquery-validation/jquery-validation/commit/5bbd80d27fc6b607d2f7f106c89522051a9fb0dd
