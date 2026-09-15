# [M] flask-cors vulnerable to log injection when the log level is set to debug

## Summary
Severity: Medium
Advisory: GHSA-84pr-m4jr-85g5
CVE: CVE-2024-1681
CWE: CWE-117
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-04-19
Source: https://github.com/advisories/GHSA-84pr-m4jr-85g5
Type: github-advisory

## Affected
- PyPI: `flask-cors` — affected >=0 <4.0.1

## Details
corydolphin/flask-cors is vulnerable to log injection when the log level is set to debug. An attacker can inject fake log entries into the log file by sending a specially crafted GET request containing a CRLF sequence in the request path. This vulnerability allows attackers to corrupt log files, potentially covering tracks of other attacks, confusing log post-processing tools, and forging log entries. The issue is due to improper output neutralization for logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1681
- https://github.com/corydolphin/flask-cors
- https://github.com/corydolphin/flask-cors/blob/40acc8092332dfed4bb54d7a4f89a6d479466de7/flask_cors/extension.py#L194
- https://github.com/pypa/advisory-database/tree/main/vulns/flask-cors/PYSEC-2024-271.yaml
- https://huntr.com/bounties/25a7a0ba-9fa2-4777-acb6-03e5539bb644
- https://lists.debian.org/debian-lts-announce/2025/05/msg00049.html
