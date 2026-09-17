# [M] CVE-2022-3560

## Summary
Severity: Medium
Advisory: CVE-2022-3560
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-02-02
Source: https://osv.dev/vulnerability/CVE-2022-3560
Type: osv

## Details
A flaw was found in pesign. The pesign package provides a systemd service used to start the pesign daemon. This service unit runs a script to set ACLs for /etc/pki/pesign and /run/pesign directories to grant access privileges to users in the 'pesign' group. However, the script doesn't check for symbolic links. This could allow an attacker to gain access to privileged files and directories via a path traversal attack.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2135420#c0
