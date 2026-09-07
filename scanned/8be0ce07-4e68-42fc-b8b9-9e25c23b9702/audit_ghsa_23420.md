# [C] Laravel Framework Deserialization Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-pfg4-p438-p874
CVE: CVE-2019-9081
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-pfg4-p438-p874
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=5.7.0 <6.20.44

## Details
The Illuminate component of Laravel Framework 5.7.x has a deserialization vulnerability that can lead to remote code execution if the content is controllable, related to the `__destruct` method of the PendingCommand class in `PendingCommand.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9081
- https://github.com/Laworigin/Laworigin.github.io/blob/master/2019/02/21/laravelv5-7%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96rce/index.html
- https://github.com/laravel/framework
- https://github.com/laravel/framework/discussions/40184
- https://laworigin.github.io/2019/02/21/laravelv5-7%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96rce
