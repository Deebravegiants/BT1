# [M] CVE-2024-49395

## Summary
Severity: Medium
Advisory: CVE-2024-49395
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-11-12
Source: https://osv.dev/vulnerability/CVE-2024-49395
Type: osv

## Details
In mutt and neomutt, PGP encryption does not use the --hidden-recipient mode which may leak the Bcc email header field by inferring from the recipients info.

## References
- https://access.redhat.com/security/cve/CVE-2024-49395
- https://bugzilla.redhat.com/show_bug.cgi?id=2325332
