# [H] CVE-2019-11278

## Summary
Severity: High
Advisory: CVE-2019-11278
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-26
Source: https://osv.dev/vulnerability/CVE-2019-11278
Type: osv

## Details
CF UAA versions prior to 74.1.0, allow external input to be directly queried against. A remote malicious user with 'client.write' and 'groups.update' can craft a SCIM query, which leaks information that allows an escalation of privileges, ultimately allowing the malicious user to gain control of UAA scopes they should not have.

## References
- https://www.cloudfoundry.org/blog/cve-2019-11278
