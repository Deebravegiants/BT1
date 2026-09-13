# [C] CVE-2024-31510

## Summary
Severity: Critical
Advisory: CVE-2024-31510
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2024-31510
Type: osv

## Details
An issue in Open Quantum Safe liboqs v.10.0 allows a remote attacker to escalate privileges via the crypto_sign_signature parameter in the /pqcrystals-dilithium-standard_ml-dsa-44-ipd_avx2/sign.c component.

## References
- https://gist.github.com/liang-junkai/a9fc693f8bdf176e9d9f56773bf20703
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31510.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31510
- https://github.com/liang-junkai/Fault-injection-of-ML-DSA
- https://github.com/open-quantum-safe/liboqs
