# [H] Improper Certificate Validation in Apache IoTDB

## Summary
Severity: High
Advisory: GHSA-wc6f-cjcp-cc33
CVE: CVE-2020-1952
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-wc6f-cjcp-cc33
Type: github-advisory

## Affected
- Maven: `org.apache.iotdb:iotdb-parent` — affected >=0 <0.9.2

## Details
An issue was found in Apache IoTDB .9.0 to 0.9.1 and 0.8.0 to 0.8.2. When starting IoTDB, the JMX port 31999 is exposed with no certification.Then, clients could execute code remotely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1952
- https://lists.apache.org/thread.html/r3d2ff899ead64d2952fdc1fbb1f520ca42011ed2b4c7f786e921f6b9%40%3Cdev.iotdb.apache.org%3E
