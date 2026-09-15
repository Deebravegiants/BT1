# [M] CVE-2020-16248

## Summary
Severity: Medium
Advisory: CVE-2020-16248
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2020-08-09
Source: https://osv.dev/vulnerability/CVE-2020-16248
Type: osv

## Details
Prometheus Blackbox Exporter through 0.17.0 allows /probe?target= SSRF. NOTE: follow-on discussion suggests that this might plausibly be interpreted as both intended functionality and also a vulnerability

## References
- https://prometheus.io/docs/operating/security/#exporters
- https://seclists.org/oss-sec/2020/q3/94
- https://www.openwall.com/lists/oss-security/2020/08/08/12
- https://www.openwall.com/lists/oss-security/2020/08/08/3
- https://github.com/prometheus/blackbox_exporter/issues/669
