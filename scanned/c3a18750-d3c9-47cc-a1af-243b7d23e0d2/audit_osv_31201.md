# [C] Buffer overread in domain name matching

## Summary
Severity: Critical
Advisory: CVE-2024-5991
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2024-08-27
Source: https://osv.dev/vulnerability/CVE-2024-5991
Type: osv

## Details
In function MatchDomainName(), input param str is treated as a NULL terminated string despite being user provided and unchecked. Specifically, the function X509_check_host() takes in a pointer and length to check against, with no requirements that it be NULL terminated. If a caller was attempting to do a name check on a non-NULL terminated buffer, the code would read beyond the bounds of the input array until it found a NULL terminator.This issue affects wolfSSL: through 5.7.0.

## References
- https://https://github.com/wolfSSL/wolfssl/pull/7604
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5991.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5991
- https://github.com/wolfSSL/wolfssl/pull/7604
