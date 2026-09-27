# [H] CVE-2021-3859

## Summary
Severity: High
Advisory: CVE-2021-3859
Aliases: GHSA-339q-62wm-c39w
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-26
Source: https://osv.dev/vulnerability/CVE-2021-3859
Type: osv

## Details
A flaw was found in Undertow that tripped the client-side invocation timeout with certain calls made over HTTP2. This flaw allows an attacker to carry out denial of service attacks.

## References
- https://access.redhat.com/security/cve/CVE-2021-3859
- https://github.com/undertow-io/undertow/pull/1296
- https://security.netapp.com/advisory/ntap-20221201-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=2010378
- https://github.com/undertow-io/undertow/commit/e43f0ada3f4da6e8579e0020cec3cb1a81e487c2
- https://issues.redhat.com/browse/UNDERTOW-1979
