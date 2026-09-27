# [H] CVE-2018-1131

## Summary
Severity: High
Advisory: CVE-2018-1131
Aliases: GHSA-qqfc-m9hc-pqv3
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-15
Source: https://osv.dev/vulnerability/CVE-2018-1131
Type: osv

## Details
Infinispan permits improper deserialization of trusted data via XML and JSON transcoders under certain server configurations. A user with authenticated access to the server could send a malicious object to a cache configured to accept certain types of objects, achieving code execution and possible further attacks. Versions 9.0.3.Final, 9.1.7.Final, 8.2.10.Final, 9.2.2.Final, 9.3.0.Alpha1 are believed to be affected.

## References
- http://www.securityfocus.com/bid/104218
- https://access.redhat.com/errata/RHSA-2018:1833
- https://access.redhat.com/errata/RHSA-2019:3892
- https://bugzilla.redhat.com/show_bug.cgi?id=1576492
