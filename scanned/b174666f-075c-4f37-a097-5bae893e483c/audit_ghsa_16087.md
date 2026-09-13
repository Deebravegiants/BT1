# [C] codechecker authentication method confusion vulnerability allows logging in as the built-in root user from an external service

## Summary
Severity: Critical
Advisory: GHSA-fpm5-2wcj-vfr7
CVE: CVE-2024-10082
CWE: CWE-305
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-11-06
Source: https://github.com/advisories/GHSA-fpm5-2wcj-vfr7
Type: github-advisory

## Affected
- PyPI: `codechecker` — affected >=0 <6.24.2

## Details
### Summary
Authentication method confusion allows logging in as the built-in root user from an external service. The built-in root user is generated in a weak manner, cannot be disabled, and has universal access. 

### Details
Until CodeChecker version 6.24.1 there was an auto-generated super-user account that could not be disabled.
The attacker needs to know only the username of the root user.

This root user is unconditionally assigned superuser permissions.

Which means that if any user via any service logs in with the root user's username, they will unconditionally have superuser permissions on the CodeChecker instance.

The name of the user name can be found in `root.user` file in the CodeChecker configuration directory.
You can check if you are impacted by checking the existence of this user in the external authentication services (e.g. LDAP, PAM etc.).

### Impact
This vulnerability allows an attacker who can create an account on an enabled external authentication service, to log in as the root user, and access and control everything that can be controlled via the web interface.
The attacker needs to acquire the username of the root user to be successful.

## References
- https://github.com/Ericsson/codechecker/security/advisories/GHSA-fpm5-2wcj-vfr7
- https://nvd.nist.gov/vuln/detail/CVE-2024-10082
- https://github.com/Ericsson/codechecker/commit/866f3796d01f3158c49b87ccae3e09c0807c1c7b
- https://github.com/Ericsson/codechecker
- https://github.com/pypa/advisory-database/tree/main/vulns/codechecker/PYSEC-2024-183.yaml
