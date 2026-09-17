# [C] DataEase: Quartz Deserialization → Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-40901
Aliases: GHSA-gm5q-g72w-c466
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-40901
Type: osv

## Details
DataEase is an open-source data visualization and analytics platform. Versions 2.10.20 and below ship the legacy velocity-1.7.jar, which pulls in commons-collections-3.2.1.jar containing the InvokerTransformer deserialization gadget chain. Quartz 2.3.2, also bundled in the application, deserializes job data BLOBs from the qrtz_job_details table using ObjectInputStream with no deserialization filter or class allowlist. An authenticated attacker who can write to the Quartz job table, such as through the previously described SQL injection in previewSql, can replace a scheduled job's JOB_DATA with a malicious CommonsCollections6 gadget chain payload. When the Quartz cron trigger fires, the payload is deserialized and executes arbitrary commands as root inside the container, achieving full remote code execution. This issue has been fixed in version 2.10.21.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40901.json
- https://github.com/dataease/dataease/security/advisories/GHSA-gm5q-g72w-c466
- https://nvd.nist.gov/vuln/detail/CVE-2026-40901
