# [C] User authentication bypass in wolfSSH server

## Summary
Severity: Critical
Advisory: CVE-2024-2873
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2024-2873
Type: osv

## Details
A vulnerability was found in wolfSSH's server-side state machine before versions 1.4.17. A malicious client could create channels without first performing user authentication, resulting in unauthorized access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2873.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2873
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/wolfSSL/wolfssh/pull/670
- https://github.com/wolfSSL/wolfssh/pull/671
- https://github.com/wolfSSL/wolfssh
