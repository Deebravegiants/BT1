# [H] CVE-2022-40304

## Summary
Severity: High
Advisory: CVE-2022-40304
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-23
Source: https://osv.dev/vulnerability/CVE-2022-40304
Type: osv

## Details
An issue was discovered in libxml2 before 2.10.3. Certain invalid XML entity definitions can corrupt a hash table key, potentially leading to subsequent logic errors. In one case, a double-free can be provoked.

## References
- https://gitlab.gnome.org/GNOME/libxml2/-/tags
- https://gitlab.gnome.org/GNOME/libxml2/-/tags/v2.10.3
- https://support.apple.com/kb/HT213531
- https://support.apple.com/kb/HT213533
- https://support.apple.com/kb/HT213534
- https://support.apple.com/kb/HT213535
- https://support.apple.com/kb/HT213536
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40304.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-40304
- https://security.netapp.com/advisory/ntap-20221209-0003/
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/1b41ec4e9433b05bb0376be4725804c54ef1d80b
- http://seclists.org/fulldisclosure/2022/Dec/21
- http://seclists.org/fulldisclosure/2022/Dec/24
- http://seclists.org/fulldisclosure/2022/Dec/25
- http://seclists.org/fulldisclosure/2022/Dec/26
- http://seclists.org/fulldisclosure/2022/Dec/27
