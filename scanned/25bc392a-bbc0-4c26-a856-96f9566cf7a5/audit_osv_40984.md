# [H] MISP remote code execution via arbitrary rdkafka configuration path

## Summary
Severity: High
Advisory: CVE-2026-56447
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-56447
Type: osv

## Details
MISP allowed an authenticated site administrator to set the Kafka_rdkafka_config setting to an arbitrary filesystem path. MISP subsequently parsed the referenced INI file and passed its options to rdkafka. A crafted attacker-controlled configuration file could use rdkafka options such as plugin.library.paths to load an external library, resulting in arbitrary code execution with the privileges of the MISP process. An attacker could leverage a MISP-writable location, such as an uploaded file or administrative image, to host the malicious configuration file.

The issue is fixed by restricting the setting to absolute .ini files located only in approved configuration directories outside the webroot and MISP upload targets.

## References
- https://github.com/MISP/MISP/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56447.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56447
- https://github.com/MISP/MISP/commit/9600d486ccfc98388e13897fd954350cebac5fb0
