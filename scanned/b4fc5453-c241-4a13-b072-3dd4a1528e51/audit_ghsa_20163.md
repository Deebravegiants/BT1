# [M] Cross site scripting in Elefant CMS

## Summary
Severity: Medium
Advisory: GHSA-xwj7-29j7-rw76
CVE: CVE-2017-20057
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-21
Source: https://github.com/advisories/GHSA-xwj7-29j7-rw76
Type: github-advisory

## Affected
- Packagist: `elefant/cms` — affected >=0 <1.3.13

## Details
A vulnerability classified as problematic has been found in Elefant CMS 1.3.12-RC. Affected is an unknown function. The manipulation of the argument username leads to basic cross site scripting (Persistent). It is possible to launch the attack remotely. Upgrading to version 1.3.13 is able to address this issue. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-20057
- https://github.com/jbroadway/elefant
- https://vuldb.com/?id.97254
- http://seclists.org/fulldisclosure/2017/Feb/36
