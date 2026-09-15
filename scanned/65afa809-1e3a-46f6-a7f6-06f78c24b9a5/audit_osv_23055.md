# [C] CVE-2022-42905

## Summary
Severity: Critical
Advisory: CVE-2022-42905
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-11-06
Source: https://osv.dev/vulnerability/CVE-2022-42905
Type: osv

## Details
In wolfSSL before 5.5.2, if callback functions are enabled (via the WOLFSSL_CALLBACKS flag), then a malicious TLS 1.3 client or network attacker can trigger a buffer over-read on the heap of 5 bytes. (WOLFSSL_CALLBACKS is only intended for debugging.)

## References
- http://packetstormsecurity.com/files/170610/wolfSSL-WOLFSSL_CALLBACKS-Heap-Buffer-Over-Read.html
- https://github.com/wolfSSL/wolfssl/releases/tag/v5.5.2-stable
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/42xxx/CVE-2022-42905.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-42905
- https://github.com/wolfSSL/wolfssl/releases
- http://seclists.org/fulldisclosure/2023/Jan/11
- https://blog.trailofbits.com/2023/01/12/wolfssl-vulnerabilities-tlspuffin-fuzzing-ssh/
