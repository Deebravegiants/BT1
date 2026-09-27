# [M] CVE-2023-6277

## Summary
Severity: Medium
Advisory: CVE-2023-6277
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-11-24
Source: https://osv.dev/vulnerability/CVE-2023-6277
Type: osv

## Details
An out-of-memory flaw was found in libtiff. Passing a crafted tiff file to TIFFOpen() API may allow a remote attacker to cause a denial of service via a craft input with size smaller than 379 KB.

## References
- http://seclists.org/fulldisclosure/2024/Jul/17
- http://seclists.org/fulldisclosure/2024/Jul/18
- http://seclists.org/fulldisclosure/2024/Jul/21
- http://seclists.org/fulldisclosure/2024/Jul/22
- https://support.apple.com/kb/HT214116
- http://seclists.org/fulldisclosure/2024/Jul/20
- http://seclists.org/fulldisclosure/2024/Jul/23
- https://support.apple.com/kb/HT214117
- https://support.apple.com/kb/HT214120
- https://support.apple.com/kb/HT214122
- https://support.apple.com/kb/HT214123
- https://support.apple.com/kb/HT214124
- https://support.apple.com/kb/HT214119
- http://seclists.org/fulldisclosure/2024/Jul/16
- http://seclists.org/fulldisclosure/2024/Jul/19
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WJIN6DTSL3VODZUGWEUXLEL5DR53EZMV/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Y7ZGN2MZXJ6E57W3L4YBM3ZPAU3T7T5C/
- https://support.apple.com/kb/HT214118
- https://access.redhat.com/security/cve/CVE-2023-6277
- https://security.netapp.com/advisory/ntap-20240119-0002/
