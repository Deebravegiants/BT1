# [M] CVE-2019-17023

## Summary
Severity: Medium
Advisory: CVE-2019-17023
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/CVE-2019-17023
Type: osv

## Details
After a HelloRetryRequest has been sent, the client may negotiate a lower protocol that TLS 1.3, resulting in an invalid state transition in the TLS State Machine. If the client gets into this state, incoming Application Data records will be ignored. This vulnerability affects Firefox < 72.

## References
- https://usn.ubuntu.com/4234-1/
- https://usn.ubuntu.com/4397-1/
- https://www.debian.org/security/2020/dsa-4726
- https://www.mozilla.org/security/advisories/mfsa2020-01/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1590001
