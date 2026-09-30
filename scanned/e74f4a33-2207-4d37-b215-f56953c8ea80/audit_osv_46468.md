# [C] CVE-2011-4120

## Summary
Severity: Critical
Advisory: CVE-2011-4120
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2011-4120
Type: osv

## Details
Yubico PAM Module before 2.10 performed user authentication when 'use_first_pass' PAM configuration option was not used and the module was configured as 'sufficient' in the PAM configuration. A remote attacker could use this flaw to circumvent common authentication process and obtain access to the account in question by providing a NULL value (pressing Ctrl-D keyboard sequence) as the password string.

## References
- https://access.redhat.com/security/cve/cve-2011-4120
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-4120
- https://security-tracker.debian.org/tracker/CVE-2011-4120
- https://www.openwall.com/lists/oss-security/2011/11/07/6
- https://www.openwall.com/lists/oss-security/2011/11/07/6
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-4120
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-4120
- https://access.redhat.com/security/cve/cve-2011-4120
