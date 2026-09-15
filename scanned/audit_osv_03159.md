# [H] ALPINE-CVE-2024-6345

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-6345
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-6345
Type: osv

## Affected
- Alpine:v3.17: `py3-setuptools` — affected >=0 <70.3.0-r0
- Alpine:v3.18: `py3-setuptools` — affected >=0 <70.3.0-r0
- Alpine:v3.19: `py3-setuptools` — affected >=0 <70.3.0-r0
- Alpine:v3.20: `py3-setuptools` — affected >=0 <70.3.0-r0
- Alpine:v3.21: `py3-setuptools` — affected >=0 <70.3.0-r0
- Alpine:v3.22: `py3-setuptools` — affected >=0 <70.3.0-r0
- Alpine:v3.23: `py3-setuptools` — affected >=0 <70.3.0-r0
- Alpine:v3.24: `py3-setuptools` — affected >=0 <70.3.0-r0

## Details
A vulnerability in the package_index module of pypa/setuptools versions up to 69.1.1 allows for remote code execution via its download functions. These functions, which are used to download packages from URLs provided by users or retrieved from package index servers, are susceptible to code injection. If these functions are exposed to user-controlled inputs, such as package URLs, they can execute arbitrary commands on the system. The issue is fixed in version 70.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-6345
