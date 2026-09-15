# [H] CVE-2024-36611

## Summary
Severity: High
Advisory: CVE-2024-36611
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-29
Source: https://osv.dev/vulnerability/CVE-2024-36611
Type: osv

## Details
In Symfony v7.07, a security vulnerability was identified in the FormLoginAuthenticator component, where it failed to adequately handle cases where the username or password field of a login request is empty. This flaw could lead to various security risks, including improper authentication logic handling or denial of service. NOTE: the Supplier has concluded that this is a false report.

## References
- https://gist.github.com/1047524396/3581425e0911b716cf8ce4fa30e41e6c
- https://github.com/symfony/symfony/blob/v7.0.7/src/Symfony/Component/Security/Http/Authenticator/FormLoginAuthenticator.php#L132
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36611.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36611
- https://github.com/symfony/symfony/issues/59077#issuecomment-2513935018
- https://github.com/github/advisory-database/pull/5046
- https://github.com/symfony/symfony/commit/a804ca15fcad279d7727b91d12a667fd5b925995
