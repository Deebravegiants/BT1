# [M] CVE-2025-43703

## Summary
Severity: Medium
Advisory: CVE-2025-43703
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-43703
Type: osv

## Details
An issue was discovered in Ankitects Anki through 25.02. A crafted shared deck can result in attacker-controlled access to the internal API (even though the attacker has no knowledge of an API key) through approaches such as scripts or the SRC attribute of an IMG element. NOTE: this issue exists because of an incomplete fix for CVE-2024-32484.

## References
- https://github.com/ankitects/anki/pull/3925/commits/24bca15fd3d9dc386916509eb2d4862d1184e709
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/43xxx/CVE-2025-43703.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-43703
- https://github.com/ankitects/anki/pull/3925
