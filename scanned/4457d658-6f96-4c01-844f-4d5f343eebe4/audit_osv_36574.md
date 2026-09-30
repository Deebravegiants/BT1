# [C] CVE-2026-24457

## Summary
Severity: Critical
Advisory: CVE-2026-24457
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-24457
Type: osv

## Details
An unsafe parsing of OpenMQ's configuration, allows a remote attacker to read arbitrary files from a MQ Broker's server. A full exploitation could read unauthorized files of the OpenMQ’s host OS. In some scenarios RCE could be achieved.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24457.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24457
- https://gitlab.eclipse.org/security/cve-assignment/-/issues/84
- https://github.com/eclipse-ee4j/openmq
