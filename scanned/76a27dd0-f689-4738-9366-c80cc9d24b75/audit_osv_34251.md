# [M] CVE-2025-56608

## Summary
Severity: Medium
Advisory: CVE-2025-56608
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2025-09-03
Source: https://osv.dev/vulnerability/CVE-2025-56608
Type: osv

## Details
The SourceCodester Android application "Corona Virus Tracker App India" 1.0 uses MD5 for digest authentication in `OkHttpClientWrapper.java`. The `handleDigest()` function employs `MessageDigest.getInstance("MD5")` to hash credentials. MD5 is a broken cryptographic algorithm known to allow hash collisions. This makes the authentication mechanism vulnerable to replay, spoofing, or brute-force attacks, potentially leading to unauthorized access. The vulnerability corresponds to CWE-327 and aligns with OWASP M5: Insufficient Cryptography and MASVS MSTG-CRYPTO-4.

## References
- https://github.com/MobSF/owasp-mstg/blob/master/Document/0x04g-Testing-Cryptography.md#identifying-insecure-andor-deprecated-cryptographic-algorithms-mstg-crypto-4
- https://www.sourcecodester.com/android/14292/android-corona-virus-tracker-app-india-using-b4a.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/56xxx/CVE-2025-56608.json
- https://github.com/anonaninda/Aninda-security-advisories/blob/main/CVE-2025-56608.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-56608
