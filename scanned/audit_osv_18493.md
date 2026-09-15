# [M] CVE-2020-28002

## Summary
Severity: Medium
Advisory: CVE-2020-28002
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-11-02
Source: https://osv.dev/vulnerability/CVE-2020-28002
Type: osv

## Details
In SonarQube 8.4.2.36762, an external attacker can achieve authentication bypass through SonarScanner. With an empty value for the -D sonar.login option, anonymous authentication is forced. This allows creating and overwriting public and private projects via the /api/ce/submit endpoint.

## References
- https://csl.com.co/sonarqube-auditando-al-auditor-parte-ii/
