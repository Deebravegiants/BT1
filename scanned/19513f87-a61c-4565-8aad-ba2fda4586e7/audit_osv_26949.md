# [H] Improper Export of Android Application Components in SAP EMARSYS SDK ANDROID

## Summary
Severity: High
Advisory: CVE-2023-6542
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-12-12
Source: https://osv.dev/vulnerability/CVE-2023-6542
Type: osv

## Details
Due to lack of proper authorization checks in Emarsys SDK for Android, an attacker can call a particular activity and can forward himself web pages and/or deep links without any validation directly from the host application. On successful attack, an attacker could navigate to arbitrary URL including application deep links on the device.

## References
- https://me.sap.com/notes/3406244
- https://www.sap.com/documents/2022/02/fa865ea4-167e-0010-bca6-c68f7e60039b.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6542.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6542
