# [M] Vesta Control Panel sed main.sh argument injection

## Summary
Severity: Medium
Advisory: CVE-2022-3967
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-11-13
Source: https://osv.dev/vulnerability/CVE-2022-3967
Type: osv

## Details
A vulnerability, which was classified as critical, was found in Vesta Control Panel. Affected is an unknown function of the file func/main.sh of the component sed Handler. The manipulation leads to argument injection. An attack has to be approached locally. The name of the patch is 39561c32c12cabe563de48cc96eccb9e2c655e25. It is recommended to apply a patch to fix this issue. VDB-213546 is the identifier assigned to this vulnerability.

## References
- https://vuldb.com/?id.213546
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3967.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3967
- https://github.com/serghey-rodin/vesta/commit/39561c32c12cabe563de48cc96eccb9e2c655e25
