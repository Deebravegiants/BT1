# [H] CVE-2024-38952

## Summary
Severity: High
Advisory: CVE-2024-38952
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-38952
Type: osv

## Details
PX4-Autopilot v1.14.3 was discovered to contain a buffer overflow via the topic_name parameter at /logger/logged_topics.cpp.

## References
- https://github.com/PX4/PX4-Autopilot/blob/main/src/modules/logger/logged_topics.cpp#L440
- https://github.com/PX4/PX4-Autopilot/blob/main/src/modules/logger/logged_topics.cpp#L561
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38952.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38952
- https://github.com/PX4/PX4-Autopilot/issues/23258
