# [H] Heap buffer overflow in vim_strncpy find_word in vim/vim

## Summary
Severity: High
Advisory: CVE-2022-1621
CVSS: 7.3 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:H)
Published: 2022-05-09
Source: https://osv.dev/vulnerability/CVE-2022-1621
Type: osv

## Details
Heap buffer overflow in vim_strncpy find_word in GitHub repository vim/vim prior to 8.2.4919. This vulnerability is capable of crashing software, Bypass Protection Mechanism, Modify Memory, and possible remote execution

## References
- https://huntr.dev/bounties/520ce714-bfd2-4646-9458-f52cd22bb2fb
- https://support.apple.com/kb/HT213488
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1621.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HIP7KG7TVS5YF3QREAY2GOGUT3YUBZAI/
- https://nvd.nist.gov/vuln/detail/CVE-2022-1621
- https://security.gentoo.org/glsa/202208-32
- https://security.gentoo.org/glsa/202305-16
- https://github.com/vim/vim/commit/7c824682d2028432ee082703ef0ab399867a089b
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/41
- https://lists.debian.org/debian-lts-announce/2022/05/msg00022.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00032.html
