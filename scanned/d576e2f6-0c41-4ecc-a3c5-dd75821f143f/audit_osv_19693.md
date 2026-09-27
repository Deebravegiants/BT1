# [C] CVE-2021-24028

## Summary
Severity: Critical
Advisory: CVE-2021-24028
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-14
Source: https://osv.dev/vulnerability/CVE-2021-24028
Type: osv

## Details
An invalid free in Thrift's table-based serialization can cause the application to crash or potentially result in code execution or other undesirable effects. This issue affects Facebook Thrift prior to v2021.02.22.00.

## References
- https://www.facebook.com/security/advisories/cve-2021-24028
- https://github.com/facebook/fbthrift/commit/bfda1efa547dce11a38592820916db01b05b9339
