# [C] Unauthenticated remote code execution in Ignition

## Summary
Severity: Critical
Advisory: GHSA-4qwp-7c67-jmcc
CVE: CVE-2021-3129
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-4qwp-7c67-jmcc
Type: github-advisory

## Affected
- Packagist: `facade/ignition` — affected >=2.5.0 <2.5.2
- Packagist: `facade/ignition` — affected >=2.0.0 <2.4.2
- Packagist: `facade/ignition` — affected >=1.7.0 <1.16.14
- Packagist: `facade/ignition` — affected >=0 <1.6.15

## Details
Ignition before 2.5.2, as used in Laravel and other products, allows unauthenticated remote attackers to execute arbitrary code because of insecure usage of file_get_contents() and file_put_contents(). This is exploitable on sites using debug mode with Laravel before 8.4.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3129
- https://github.com/facade/ignition/pull/334
- https://github.com/facade/ignition/commit/11ffca14abd22db779d90b12e193f8000f6d184b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/facade/ignition/CVE-2021-3129.yaml
- https://github.com/facade/ignition
- https://www.ambionics.io/blog/laravel-debug-rce
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-3129
- http://packetstormsecurity.com/files/162094/Ignition-2.5.1-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/165999/Ignition-Remote-Code-Execution.html
