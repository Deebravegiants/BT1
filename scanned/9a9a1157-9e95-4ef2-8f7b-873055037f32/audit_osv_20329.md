# [M] CVE-2021-32801

## Summary
Severity: Medium
Advisory: CVE-2021-32801
Aliases: GHSA-mcpf-v65v-359h
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-32801
Type: osv

## Details
Nextcloud server is an open source, self hosted personal cloud. In affected versions logging of exceptions may have resulted in logging potentially sensitive key material for the Nextcloud Encryption-at-Rest functionality. It is recommended that the Nextcloud Server is upgraded to 20.0.12, 21.0.4 or 22.1.0. If upgrading is not an option users are advised to disable system logging to resolve this issue until such time that an upgrade can be performed Note that ff you do not use the Encryption-at-Rest functionality of Nextcloud you are not affected by this bug.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-mcpf-v65v-359h
- https://github.com/nextcloud/server/pull/28082
- https://security.gentoo.org/glsa/202208-17
- https://hackerone.com/reports/1251776
