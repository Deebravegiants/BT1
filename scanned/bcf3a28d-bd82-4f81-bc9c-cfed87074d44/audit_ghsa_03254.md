# [C] OS Command Injection in pulverizr

## Summary
Severity: Critical
Advisory: GHSA-fmf5-j5j9-99pp
CVE: CVE-2020-7604
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-fmf5-j5j9-99pp
Type: github-advisory

## Affected
- npm: `pulverizr` — affected >=0

## Details
pulverizr through 0.7.0 allows execution of arbitrary commands. Within `lib/job.js`, the variable `filename` can be controlled by the attacker. This function uses the variable &quot;filename&quot; to construct the argument of the exec call without any sanitization. In order to successfully exploit this vulnerability, an attacker will need to create a new file with the same name as the attack command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7604
- https://github.com/bentruyman/pulverizr/blob/master/lib/job.js#L73
- https://snyk.io/vuln/SNYK-JS-PULVERIZR-560122
