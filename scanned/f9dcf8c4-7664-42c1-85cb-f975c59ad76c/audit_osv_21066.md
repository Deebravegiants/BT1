# [H] CVE-2021-40348

## Summary
Severity: High
Advisory: CVE-2021-40348
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-11-01
Source: https://osv.dev/vulnerability/CVE-2021-40348
Type: osv

## Details
Spacewalk 2.10, and derivatives such as Uyuni 2021.08, allows code injection. rhn-config-satellite.pl doesn't sanitize the configuration filename used to append Spacewalk-specific key-value pair. The script is intended to be run by the tomcat user account with Sudo, according to the installation setup. This can lead to the ability of an attacker to use --option to append arbitrary code to a root-owned file that eventually will be executed by the system. This is fixed in Uyuni spacewalk-admin 4.3.2-1.

## References
- http://www.openwall.com/lists/oss-security/2021/10/28/4
- https://github.com/uyuni-project/uyuni/commit/790c7388efac6923c5475e01c1ff718dffa9f052
