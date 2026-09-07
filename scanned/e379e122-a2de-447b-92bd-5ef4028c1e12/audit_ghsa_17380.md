# [M] ABP Account Module has an Open Redirect through Improper validation in its register function

## Summary
Severity: Medium
Advisory: GHSA-vfm5-cr22-jg3m
CVE: CVE-2025-65581
CWE: CWE-20, CWE-601
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-12-16
Source: https://github.com/advisories/GHSA-vfm5-cr22-jg3m
Type: github-advisory

## Affected
- NuGet: `Volo.Abp.Account.Web` — affected >=5.1.0 <10.0.0-rc.2

## Details
An open redirect vulnerability exists in the Account module in Volosoft ABP Framework >= 5.1.0 and < 10.0.0-rc.2. Improper validation of the returnUrl parameter in the register function allows an attacker to redirect users to arbitrary external domains.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65581
- https://github.com/abpframework/abp/commit/44a2dc14e933f3ce1ca93f9313d836694ab77d1d
- https://github.com/abpframework/abp/commit/a01adc58464d278ca817c4bbb6cbce30f155d0d1
- https://github.com/abpframework/abp
