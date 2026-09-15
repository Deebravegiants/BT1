# [H] CVE-2020-14365

## Summary
Severity: High
Advisory: CVE-2020-14365
Aliases: GHSA-m429-fhmv-c6q2, PYSEC-2020-209
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-09-23
Source: https://osv.dev/vulnerability/CVE-2020-14365
Type: osv

## Details
A flaw was found in the Ansible Engine, in ansible-engine 2.8.x before 2.8.15 and ansible-engine 2.9.x before 2.9.13, when installing packages using the dnf module. GPG signatures are ignored during installation even when disable_gpg_check is set to False, which is the default behavior. This flaw leads to malicious packages being installed on the system and arbitrary code executed via package installation scripts. The highest threat from this vulnerability is to integrity and system availability.

## References
- https://www.debian.org/security/2021/dsa-4950
- https://bugzilla.redhat.com/show_bug.cgi?id=1869154
