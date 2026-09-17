# [H] CVE-2019-3804

## Summary
Severity: High
Advisory: CVE-2019-3804
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-26
Source: https://osv.dev/vulnerability/CVE-2019-3804
Type: osv

## Details
It was found that cockpit before version 184 used glib's base64 decode functionality incorrectly resulting in a denial of service attack. An unauthenticated attacker could send a specially crafted request with an invalid base64-encoded cookie which could cause the web service to crash.

## References
- https://access.redhat.com/errata/RHSA-2019:1569
- https://access.redhat.com/errata/RHSA-2019:1571
- https://github.com/cockpit-project/cockpit/pull/10819
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3804
- https://github.com/cockpit-project/cockpit/commit/c51f6177576d7e12
