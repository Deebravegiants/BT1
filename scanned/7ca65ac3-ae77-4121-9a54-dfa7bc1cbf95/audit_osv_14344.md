# [C] CVE-2018-9246

## Summary
Severity: Critical
Advisory: CVE-2018-9246
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-08
Source: https://osv.dev/vulnerability/CVE-2018-9246
Type: osv

## Details
The PGObject::Util::DBAdmin module before 0.120.0 for Perl, as used in LedgerSMB through 1.5.x, insufficiently sanitizes or escapes variable values used as part of shell command execution, resulting in shell code injection via the create(), run_file(), backup(), or restore() function. The vulnerability allows unauthorized users to execute code with the same privileges as the running application.

## References
- https://archive.ledgersmb.org/ledger-smb-announce/msg00280.html
