# [C] CVE-2020-19229

## Summary
Severity: Critical
Advisory: CVE-2020-19229
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-05
Source: https://osv.dev/vulnerability/CVE-2020-19229
Type: osv

## Details
Jeesite 1.2.7 uses the apache shiro version 1.2.3 affected by CVE-2016-4437. Because of this version of the java deserialization vulnerability, an attacker could exploit the vulnerability to execute arbitrary commands via the rememberMe parameter.

## References
- https://github.com/thinkgem/jeesite/issues/490
