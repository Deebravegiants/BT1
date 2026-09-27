# [H] ALPINE-CVE-2024-6119

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-6119
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-6119
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=3.0.0 <3.0.15-r0
- Alpine:v3.18: `openssl` — affected >=3.0.0 <3.1.7-r0
- Alpine:v3.19: `openssl` — affected >=3.0.0 <3.1.7-r0
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.3.2-r0
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.3.2-r0
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.3.2-r0
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.3.2-r0
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.3.2-r0

## Details
Issue summary: Applications performing certificate name checks (e.g., TLS
clients checking server certificates) may attempt to read an invalid memory
address resulting in abnormal termination of the application process.

Impact summary: Abnormal termination of an application can a cause a denial of
service.

Applications performing certificate name checks (e.g., TLS clients checking
server certificates) may attempt to read an invalid memory address when
comparing the expected name with an `otherName` subject alternative name of an
X.509 certificate. This may result in an exception that terminates the
application program.

Note that basic certificate chain validation (signatures, dates, ...) is not
affected, the denial of service can occur only when the application also
specifies an expected DNS name, Email address or IP address.

TLS servers rarely solicit client certificates, and even when they do, they
generally don't perform a name check against a reference identifier (expected
identity), but rather extract the presented identity after checking the
certificate chain.  So TLS servers are generally not affected and the severity
of the issue is Moderate.

The FIPS modules in 3.3, 3.2, 3.1 and 3.0 are not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-6119
