# [H] RosarioSIS Stores Sensitive Data in a Mechanism without Access Control

## Summary
Severity: High
Advisory: GHSA-36cm-h8gv-mg97
CVE: CVE-2023-2665
CWE: CWE-921, CWE-922
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-19
Source: https://github.com/advisories/GHSA-36cm-h8gv-mg97
Type: github-advisory

## Affected
- Packagist: `francoisjacquet/rosariosis` — affected >=0 <11.0

## Details
RosarioSIS prior to 11.0 allows anyone, regardless of authentication status, to download and view file attachments under the `salaries` module. In addition, the file names contain a date in a `YYYY-MM-DD` format and a random six-string digit, making enumerating file names with automated tools relatively easy. This could allow an attacker to gain access to sensitive salary information. The patch for version 11.0 adds microseconds to filenames to make them harder to guess.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2665
- https://github.com/francoisjacquet/rosariosis/commit/09d5afaa6be07688ca1a7ac3b755b5438109e986
- https://github.com/francoisjacquet/rosariosis
- https://huntr.dev/bounties/42f38a84-8954-484d-b5ff-706ca0918194
