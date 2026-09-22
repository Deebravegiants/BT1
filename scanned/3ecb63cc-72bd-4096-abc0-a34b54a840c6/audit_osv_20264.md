# [M] CVE-2021-32651

## Summary
Severity: Medium
Advisory: CVE-2021-32651
Aliases: GHSA-5864-2496-4xjf
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/CVE-2021-32651
Type: osv

## Details
OneDev is a development operations platform. If the LDAP external authentication mechanism is enabled in OneDev versions 4.4.1 and prior, an attacker can manipulate a user search filter to send forged queries to the application and explore the LDAP tree using Blind LDAP Injection techniques. The specific payload depends on how the User Search Filter property is configured in OneDev. This issue was fixed in version 4.4.2.

## References
- https://github.com/theonedev/onedev/commit/4440f0c57e440488d7e653417b2547eaae8ad19c
- https://github.com/theonedev/onedev/security/advisories/GHSA-5864-2496-4xjf
