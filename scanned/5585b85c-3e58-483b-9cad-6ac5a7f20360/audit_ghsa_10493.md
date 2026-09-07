# [H] Apache DolphinScheduler vulnerable to sensitive information disclosure

## Summary
Severity: High
Advisory: GHSA-3cjc-vhfm-ffp2
CVE: CVE-2025-62188
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-3cjc-vhfm-ffp2
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler` — affected >=3.1.0 <3.2.0

## Details
An Exposure of Sensitive Information to an Unauthorized Actor vulnerability exists in Apache DolphinScheduler.

This vulnerability may allow unauthorized actors to access sensitive information, including database credentials.


This issue affects Apache DolphinScheduler versions 3.1.*.


Users are recommended to upgrade to:

  *  version ≥ 3.2.0 if using 3.1.x

As a temporary workaround, users who cannot upgrade immediately may restrict the exposed management endpoints by setting the following environment variable:


```
MANAGEMENT_ENDPOINTS_WEB_EXPOSURE_INCLUDE=health,metrics,prometheus
```

Alternatively, add the following configuration to the application.yaml file:


```
management:
   endpoints:
     web:
        exposure:
          include: health,metrics,prometheus
```

This issue has been reported as CVE-2023-48796:

 https://cveprocess.apache.org/cve5/CVE-2023-48796

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62188
- https://github.com/apache/dolphinscheduler
- https://github.com/apache/dolphinscheduler/releases/tag/3.0.2
- https://lists.apache.org/thread/ffrmkcwgr2lcz0f5nnnyswhpn3fytsvo
- https://www.cve.org/CVERecord?id=CVE-2023-48796
