# [M] Heap-based Buffer Overflow in function cmdline_erase_chars in vim/vim

## Summary
Severity: Medium
Advisory: CVE-2022-1619
CVSS: 6.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2022-05-08
Source: https://osv.dev/vulnerability/CVE-2022-1619
Type: osv

## Details
Heap-based Buffer Overflow in function cmdline_erase_chars in GitHub repository vim/vim prior to 8.2.4899. This vulnerabilities are capable of crashing software, modify memory, and possible remote execution

## References
- https://huntr.dev/bounties/b3200483-624e-4c76-a070-e246f62a7450
- https://support.apple.com/kb/HT213488
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1619.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A6BY5P7ERZS7KXSBCGFCOXLMLGWUUJIH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HIP7KG7TVS5YF3QREAY2GOGUT3YUBZAI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JUN33257RUM4RS2I4GZETKFSAXPETATG/
- https://nvd.nist.gov/vuln/detail/CVE-2022-1619
- https://security.gentoo.org/glsa/202208-32
- https://security.gentoo.org/glsa/202305-16
- https://security.netapp.com/advisory/ntap-20220930-0007/
- https://github.com/vim/vim/commit/ef02f16609ff0a26ffc6e20263523424980898fe
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/41
- https://lists.debian.org/debian-lts-announce/2022/05/msg00022.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00032.html
