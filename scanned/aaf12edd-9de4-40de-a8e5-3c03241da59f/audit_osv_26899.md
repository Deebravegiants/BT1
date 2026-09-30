# [M] Samba: heap buffer overflow with freshness tokens in the heimdal kdc

## Summary
Severity: Medium
Advisory: CVE-2023-5568
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2023-10-24
Source: https://osv.dev/vulnerability/CVE-2023-5568
Type: osv

## Details
A heap-based Buffer Overflow flaw was discovered in Samba. It could allow a remote, authenticated attacker to exploit this vulnerability to cause a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://www.samba.org/samba/history/samba-4.19.2.html
- https://access.redhat.com/security/cve/CVE-2023-5568
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5568.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5568
- https://security.netapp.com/advisory/ntap-20231124-0007/
- https://bugzilla.redhat.com/show_bug.cgi?id=2245174
- https://bugzilla.samba.org/show_bug.cgi?id=15491
