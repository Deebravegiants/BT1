# [M] CVE-2020-14332

## Summary
Severity: Medium
Advisory: CVE-2020-14332
Aliases: GHSA-j667-c2hm-f2wp, PYSEC-2020-4
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-11
Source: https://osv.dev/vulnerability/CVE-2020-14332
Type: osv

## Details
A flaw was found in the Ansible Engine when using module_args. Tasks executed with check mode (--check-mode) do not properly neutralize sensitive data exposed in the event data. This flaw allows unauthorized users to read this data. The highest threat from this vulnerability is to confidentiality.

## References
- https://www.debian.org/security/2021/dsa-4950
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14332
- https://github.com/ansible/ansible/pull/71033
