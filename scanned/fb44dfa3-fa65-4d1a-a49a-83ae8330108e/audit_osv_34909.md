# [C] SNMP Command Injection leads to RCE in Cacti

## Summary
Severity: Critical
Advisory: CVE-2025-66399
Aliases: GHSA-c7rr-2h93-7gjf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-12-02
Source: https://osv.dev/vulnerability/CVE-2025-66399
Type: osv

## Details
Cacti is an open source performance and fault management framework. Prior to 1.2.29, there is an input-validation flaw in the SNMP device configuration functionality. An authenticated Cacti user can supply crafted SNMP community strings containing control characters (including newlines) that are accepted, stored verbatim in the database, and later embedded into backend SNMP operations. In environments where downstream SNMP tooling or wrappers interpret newline-separated tokens as command boundaries, this can lead to unintended command execution with the privileges of the Cacti process. This vulnerability is fixed in 1.2.29.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66399.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-c7rr-2h93-7gjf
- https://nvd.nist.gov/vuln/detail/CVE-2025-66399
