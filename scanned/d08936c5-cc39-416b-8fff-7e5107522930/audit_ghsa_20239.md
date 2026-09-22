# [H] Unrestricted Upload of File with Dangerous Type in Elefant CMS

## Summary
Severity: High
Advisory: GHSA-mwh6-g9wx-xcx3
CVE: CVE-2017-20063
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-21
Source: https://github.com/advisories/GHSA-mwh6-g9wx-xcx3
Type: github-advisory

## Affected
- Packagist: `elefant/cms` — affected >=0 <1.3.13

## Details
A vulnerability was found in Elefant CMS 1.3.12-RC. It has been classified as critical. Affected is an unknown function of the file /filemanager/upload/drop of the component File Upload. The manipulation leads to improper privilege management. It is possible to launch the attack remotely. Upgrading to version 1.3.13 is able to address this issue. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-20063
- https://github.com/jbroadway/elefant
- https://vuldb.com/?id.97260
- http://seclists.org/fulldisclosure/2017/Feb/39
