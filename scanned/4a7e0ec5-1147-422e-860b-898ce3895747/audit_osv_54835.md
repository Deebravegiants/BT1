# [M] CVE-2024-49393

## Summary
Severity: Medium
Advisory: CVE-2024-49393
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2024-11-12
Source: https://osv.dev/vulnerability/CVE-2024-49393
Type: osv

## Details
In neomutt and mutt, the To and Cc email headers are not validated by cryptographic signing which allows an attacker that intercepts a message to change their value and include himself as a one of the recipients to compromise message confidentiality.

## References
- https://access.redhat.com/security/cve/CVE-2024-49393
- https://bugzilla.redhat.com/show_bug.cgi?id=2325317
