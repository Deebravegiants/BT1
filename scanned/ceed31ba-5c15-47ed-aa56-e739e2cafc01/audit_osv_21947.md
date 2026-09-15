# [M] NULL Pointer Dereference in function vim_regexec_string at regexp.c:2729 in vim/vim

## Summary
Severity: Medium
Advisory: CVE-2022-1620
CVSS: 6.6 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2022-05-08
Source: https://osv.dev/vulnerability/CVE-2022-1620
Type: osv

## Details
NULL Pointer Dereference in function vim_regexec_string at regexp.c:2729 in GitHub repository vim/vim prior to 8.2.4901. NULL Pointer Dereference in function vim_regexec_string at regexp.c:2729 allows attackers to cause a denial of service (application crash) via a crafted input.

## References
- https://huntr.dev/bounties/7a4c59f3-fcc0-4496-995d-5ca6acd2da51
- https://support.apple.com/kb/HT213488
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1620.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A6BY5P7ERZS7KXSBCGFCOXLMLGWUUJIH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HIP7KG7TVS5YF3QREAY2GOGUT3YUBZAI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JUN33257RUM4RS2I4GZETKFSAXPETATG/
- https://nvd.nist.gov/vuln/detail/CVE-2022-1620
- https://security.gentoo.org/glsa/202208-32
- https://security.gentoo.org/glsa/202305-16
- https://github.com/vim/vim/commit/8e4b76da1d7e987d43ca960dfbc372d1c617466f
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/41
