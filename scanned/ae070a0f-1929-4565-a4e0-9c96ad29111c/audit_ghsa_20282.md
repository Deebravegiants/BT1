# [H] Code injection in Elefant CMS

## Summary
Severity: High
Advisory: GHSA-gx6v-67qv-rhx5
CVE: CVE-2017-20064
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-21
Source: https://github.com/advisories/GHSA-gx6v-67qv-rhx5
Type: github-advisory

## Affected
- Packagist: `elefant/cms` — affected >=0 <1.3.13

## Details
A vulnerability was found in Elefant CMS 1.3.12-RC. It has been declared as critical. Affected by this vulnerability is an unknown functionality of the file /designer/add/layout. The manipulation leads to code injection. The attack can be launched remotely. Upgrading to version 1.3.13 is able to address this issue. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-20064
- https://github.com/jbroadway/elefant
- https://vuldb.com/?id.97261
- http://seclists.org/fulldisclosure/2017/Feb/39
