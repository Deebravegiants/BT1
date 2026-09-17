# [M] CVE-2022-2447

## Summary
Severity: Medium
Advisory: CVE-2022-2447
CVSS: 6.6 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2022-2447
Type: osv

## Details
A flaw was found in Keystone. There is a time lag (up to one hour in a default configuration) between when security policy says a token should be revoked from when it is actually revoked. This could allow a remote administrator to secretly maintain access for longer than expected.

## References
- https://access.redhat.com/security/cve/CVE-2022-2447
- https://bugzilla.redhat.com/show_bug.cgi?id=2105419
