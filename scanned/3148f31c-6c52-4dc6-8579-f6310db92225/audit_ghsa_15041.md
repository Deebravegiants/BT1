# [H] Insecure random string generator used for sensitive data

## Summary
Severity: High
Advisory: GHSA-4248-p65p-hcrm
CVE: CVE-2023-46740
CWE: CWE-330
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-4248-p65p-hcrm
Type: github-advisory

## Affected
- Go: `github.com/cubefs/cubefs` — affected >=0 <3.3.1

## Details
CubeFS used an insecure random string generator to generate user-specific, sensitive keys used to authenticate users in a CubeFS deployment. This could allow an attacker to predict and/or guess the generated string and impersonate a user thereby obtaining higher privileges.

When CubeFS creates new users, it creates a piece of sensitive information for the user called the “accessKey”. To create the "accesKey", CubeFS uses an insecure string generator which makes it easy to guess and thereby impersonate the created user. 

An attacker could leverage the predictable random string generator and guess a users access key and impersonate the user to obtain higher privileges.

There is no evidence of this vulnerability being exploited in the wild. It was found during a security audit carried out by [Ada Logics](https://adalogics.com/) in collaboration with [OSTIF](https://ostif.org/) and the [CNCF](https://www.cncf.io/).

The issue has been fixed in v3.3.1. There is no other mitigation than to upgrade.

## References
- https://github.com/cubefs/cubefs/security/advisories/GHSA-4248-p65p-hcrm
- https://nvd.nist.gov/vuln/detail/CVE-2023-46740
- https://github.com/cubefs/cubefs/commit/8555c6402794cabdf2cc025c8bea1576122c07ba
- https://github.com/cubefs/cubefs
