# [M] CVE-2018-19046

## Summary
Severity: Medium
Advisory: CVE-2018-19046
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-11-08
Source: https://osv.dev/vulnerability/CVE-2018-19046
Type: osv

## Details
keepalived 2.0.8 didn't check for existing plain files when writing data to a temporary file upon a call to PrintData or PrintStats. If a local attacker had previously created a file with the expected name (e.g., /tmp/keepalived.data or /tmp/keepalived.stats), with read access for the attacker and write access for the keepalived process, then this potentially leaked sensitive information.

## References
- https://security.gentoo.org/glsa/201903-01
- https://bugzilla.suse.com/show_bug.cgi?id=1015141
- https://github.com/acassen/keepalived/issues/1048
