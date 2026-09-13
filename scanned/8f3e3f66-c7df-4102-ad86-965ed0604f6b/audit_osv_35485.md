# [M] CVE-2025-9955

## Summary
Severity: Medium
Advisory: CVE-2025-9955
CVSS: 5.7 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-9955
Type: osv

## Details
An improper access control vulnerability exists in WSO2 Enterprise Integrator product due to insufficient permission restrictions on internal SOAP admin services related to system logs and user-store configuration. A low-privileged user can access log data and user-store configuration details that are not intended to be exposed at that privilege level.

While no credentials or sensitive user information are exposed, this vulnerability may allow unauthorized visibility into internal operational details, which could aid in further exploitation or reconnaissance.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2025-4526/
