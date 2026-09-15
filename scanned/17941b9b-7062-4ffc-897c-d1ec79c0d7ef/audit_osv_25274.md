# [H] CVE-2023-32787

## Summary
Severity: High
Advisory: CVE-2023-32787
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-15
Source: https://osv.dev/vulnerability/CVE-2023-32787
Type: osv

## Details
The OPC UA Legacy Java Stack before 6f176f2 enables an attacker to block OPC UA server applications via uncontrolled resource consumption so that they can no longer serve client applications.

## References
- https://files.opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2023-32787.pdf
- https://github.com/OPCFoundation/UA-Java-Legacy/commit/6f176f2b445a27c157f1a32f225accc9ce8873c0
- https://github.com/OPCFoundation/UA-Java-Legacy
