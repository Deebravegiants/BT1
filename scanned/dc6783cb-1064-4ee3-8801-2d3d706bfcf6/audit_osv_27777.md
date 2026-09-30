# [C] CVE-2024-25714

## Summary
Severity: Critical
Advisory: CVE-2024-25714
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-02-11
Source: https://osv.dev/vulnerability/CVE-2024-25714
Type: osv

## Details
In Rhonabwy through 1.1.13, HMAC signature verification uses a strcmp function that is vulnerable to side-channel attacks, because it stops the comparison when the first difference is spotted in the two signatures. (The fix uses gnutls_memcmp, which has constant-time execution.)

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25714.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25714
- https://github.com/babelouest/rhonabwy/commit/f9fd9a1c77e48b514ebb3baf0360f87eef3d846e
