# [H] CVE-2020-11016

## Summary
Severity: High
Advisory: CVE-2020-11016
Aliases: GHSA-rrhh-rcgp-q2m2
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-30
Source: https://osv.dev/vulnerability/CVE-2020-11016
Type: osv

## Details
IntelMQ Manager from version 1.1.0 and before version 2.1.1 has a vulnerability where the backend incorrectly handled messages given by user-input in the "send" functionality of the Inspect-tool of the Monitor component. An attacker with access to the IntelMQ Manager could possibly use this issue to execute arbitrary code with the privileges of the webserver. Version 2.1.1 fixes the vulnerability.

## References
- https://github.com/certtools/intelmq-manager/releases/tag/2.1.1
- https://lists.cert.at/pipermail/intelmq-users/2020-April/000161.html
- https://github.com/certtools/intelmq-manager/commit/b9a2ac43a4f99d764b827108f6a99dc4a9faa013
- https://github.com/certtools/intelmq-manager/security/advisories/GHSA-rrhh-rcgp-q2m2
