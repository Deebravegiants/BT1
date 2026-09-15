# [C] CVE-2022-45141

## Summary
Severity: Critical
Advisory: CVE-2022-45141
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-06
Source: https://osv.dev/vulnerability/CVE-2022-45141
Type: osv

## Details
Since the Windows Kerberos RC4-HMAC Elevation of Privilege Vulnerability was disclosed by Microsoft on Nov 8 2022 and per RFC8429 it is assumed that rc4-hmac is weak, Vulnerable Samba Active Directory DCs will issue rc4-hmac encrypted tickets despite the target server supporting better encryption (eg aes256-cts-hmac-sha1-96).

## References
- https://www.samba.org/samba/security/CVE-2022-45141.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/45xxx/CVE-2022-45141.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-45141
- https://security.gentoo.org/glsa/202309-06
