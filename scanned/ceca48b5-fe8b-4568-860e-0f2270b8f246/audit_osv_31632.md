# [M] CVE-2025-1979

## Summary
Severity: Medium
Advisory: CVE-2025-1979
Aliases: GHSA-w4rh-fgx7-q63m, PYSEC-2025-23
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:L/SA:N)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2025-1979
Type: osv

## Details
Versions of the package ray before 2.43.0 are vulnerable to Insertion of Sensitive Information into Log File where the redis password is being logged in the standard logging. If the redis password is passed as an argument, it will be logged and could potentially leak the password.This is only exploitable if:1) Logging is enabled;2) Redis is using password authentication;3) Those logs are accessible to an attacker, who can reach that redis instance.**Note:**It is recommended that anyone who is running in this configuration should update to the latest version of Ray, then rotate their redis password.

## References
- https://security.snyk.io/vuln/SNYK-PYTHON-RAY-8745212
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1979.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1979
- https://github.com/ray-project/ray/issues/50266
- https://github.com/ray-project/ray/commit/64a2e4010522d60b90c389634f24df77b603d85d
- https://github.com/ray-project/ray/pull/50409
