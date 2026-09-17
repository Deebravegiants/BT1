# [H] Uncontrolled Resource Consumption in Apache DolphinScheduler

## Summary
Severity: High
Advisory: GHSA-qg5x-66hp-cw5p
CVE: CVE-2022-25598
CWE: CWE-1333, CWE-400
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-31
Source: https://github.com/advisories/GHSA-qg5x-66hp-cw5p
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler` — affected >=0 <2.0.5
- PyPI: `apache-dolphinscheduler` — affected >=0 <2.0.5

## Details
Apache DolphinScheduler user registration is vulnerable to Regular express Denial of Service (ReDoS) attacks. Apache DolphinScheduler users should upgrade to version 2.0.5 or higher.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25598
- https://github.com/apache/dolphinscheduler
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-dolphinscheduler/PYSEC-2022-176.yaml
- https://lists.apache.org/thread/hwnw7xr969sg5nv84wz75nfr2c76fl93
