# [H] SEGV and out of bounds memory read from malicious packet

## Summary
Severity: High
Advisory: CVE-2024-0901
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2024-0901
Type: osv

## Details
Remotely executed SEGV and out of bounds read allows malicious packet sender to crash or cause an out of bounds read via sending a malformed packet with the correct length.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0901.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0901
- https://github.com/wolfSSL/wolfssl/issues/7089
- https://github.com/wolfSSL/wolfssl/pull/7099
- https://github.com/wolfSSL/wolfssl
