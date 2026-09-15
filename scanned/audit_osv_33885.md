# [H] CVE-2025-52289

## Summary
Severity: High
Advisory: CVE-2025-52289
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-07-31
Source: https://osv.dev/vulnerability/CVE-2025-52289
Type: osv

## Details
A Broken Access Control vulnerability in MagnusBilling v7.8.5.3 allows newly registered users to gain escalated privileges by sending a crafted request to /mbilling/index.php/user/save to set their account status fom "pending" to "active" without requiring administrator approval.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52289.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52289
- https://github.com/magnussolution/magnusbilling7/commit/f886330e9e9216a3830775610a4a83f970c08e8d
- https://github.com/Madhav-Bhardwaj/CVE-2025-52289
