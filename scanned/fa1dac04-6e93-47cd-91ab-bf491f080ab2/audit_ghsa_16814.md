# [M] Jberet: jberet-core logging database credentials

## Summary
Severity: Medium
Advisory: GHSA-9wmf-xf3h-r8pr
CVE: CVE-2024-1102
CWE: CWE-200, CWE-523, CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-25
Source: https://github.com/advisories/GHSA-9wmf-xf3h-r8pr
Type: github-advisory

## Affected
- Maven: `org.jberet:jberet-core` — affected >=0 <2.2.1.Final

## Details
A vulnerability was found in jberet-core logging. An exception in 'dbProperties' might display user credentials such as the username and password for the database-connection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1102
- https://github.com/jberet/jsr352/issues/452
- https://github.com/jberet/jsr352/commit/eeef999663d7da0e372aeeeac26ecf7201a3121d
- https://access.redhat.com/errata/RHSA-2024:1677
- https://access.redhat.com/errata/RHSA-2024:3580
- https://access.redhat.com/errata/RHSA-2024:3581
- https://access.redhat.com/errata/RHSA-2024:3583
- https://access.redhat.com/security/cve/CVE-2024-1102
- https://bugzilla.redhat.com/show_bug.cgi?id=2262060
- https://github.com/jberet/jsr352
