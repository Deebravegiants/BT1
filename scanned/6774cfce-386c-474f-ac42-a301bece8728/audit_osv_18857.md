# [C] CVE-2020-36619

## Summary
Severity: Critical
Advisory: CVE-2020-36619
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-19
Source: https://osv.dev/vulnerability/CVE-2020-36619
Type: osv

## Details
A vulnerability was found in multimon-ng. It has been rated as critical. This issue affects the function add_ch of the file demod_flex.c. The manipulation of the argument ch leads to format string. Upgrading to version 1.2.0 is able to address this issue. The name of the patch is e5a51c508ef952e81a6da25b43034dd1ed023c07. It is recommended to upgrade the affected component. The identifier VDB-216269 was assigned to this vulnerability.

## References
- https://github.com/EliasOenal/multimon-ng/releases/tag/1.2.0
- https://vuldb.com/?id.216269
- https://github.com/EliasOenal/multimon-ng/commit/e5a51c508ef952e81a6da25b43034dd1ed023c07
- https://github.com/EliasOenal/multimon-ng/pull/160
