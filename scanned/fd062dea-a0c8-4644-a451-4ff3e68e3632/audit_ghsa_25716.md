# [H] Missing input validation can lead to command execution in composer

## Summary
Severity: High
Advisory: GHSA-x7cr-6qr6-2hh6
CVE: CVE-2022-24828
CWE: CWE-20, CWE-88, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-x7cr-6qr6-2hh6
Type: github-advisory

## Affected
- Packagist: `composer/composer` — affected >=0 <1.10.26
- Packagist: `composer/composer` — affected >=2.0 <2.2.12
- Packagist: `composer/composer` — affected >=2.3 <2.3.5

## Details
The Composer method `VcsDriver::getFileContent()` with user-controlled `$file` or `$identifier` arguments is susceptible to an argument injection vulnerability. It can be leveraged to gain arbitrary command execution if the Mercurial or the Git driver are used.

This led to a vulnerability on Packagist.org and Private Packagist, i.e., using the composer.json `readme` field as a vector for injecting parameters into the `$file` argument for the Mercurial driver or via the `$identifier` argument for the Git and Mercurial drivers.

Composer itself can be attacked through branch names by anyone controlling a Git or Mercurial repository, which is explicitly listed by URL in a project's composer.json.

To the best of our knowledge, this was not actively exploited. The vulnerability has been patched on Packagist.org and Private Packagist within a day of the vulnerability report.

## References
- https://github.com/composer/composer/security/advisories/GHSA-x7cr-6qr6-2hh6
- https://nvd.nist.gov/vuln/detail/CVE-2022-24828
- https://github.com/composer/composer/commit/2c40c53637c5c7e43fff7c09d3d324d632734709
- https://github.com/FriendsOfPHP/security-advisories/blob/master/composer/composer/CVE-2022-24828.yaml
- https://github.com/composer/composer
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/625MT3IKWKFVIWLSYZFSXHVUA2LES7YQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GWT6LDSRY7SFMTDZWJ4MS2ZBXHL7VQEF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QD7JQWL6C4GVROO25DTXWYWM6BPOPPCG
- https://www.tenable.com/security/tns-2022-09
