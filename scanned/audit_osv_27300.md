# [M] AES T-Table sub-cache-line leakage

## Summary
Severity: Medium
Advisory: CVE-2024-1543
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-08-29
Source: https://osv.dev/vulnerability/CVE-2024-1543
Type: osv

## Details
The side-channel protected T-Table implementation in wolfSSL up to version 5.6.5 protects against a side-channel attacker with cache-line resolution. In a controlled environment such as Intel SGX, an attacker can gain a per instruction sub-cache-line resolution allowing them to break the cache-line-level protection. For details on the attack refer to:  https://doi.org/10.46586/tches.v2024.i1.457-500

## References
- https://github.com/wolfSSL/wolfssl/blob/master/ChangeLog.md#wolfssl-release-566-dec-19-2023
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1543.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1543
- https://github.com/wolfSSL/wolfssl
