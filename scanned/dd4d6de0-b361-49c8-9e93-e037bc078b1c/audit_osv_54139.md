# [H] CVE-2023-39928

## Summary
Severity: High
Advisory: CVE-2023-39928
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-10-06
Source: https://osv.dev/vulnerability/CVE-2023-39928
Type: osv

## Details
A use-after-free vulnerability exists in the MediaRecorder API of Webkit WebKitGTK 2.40.5. A specially crafted web page can abuse this vulnerability to cause memory corruption and potentially arbitrary code execution. A user would need to to visit a malicious webpage to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1831
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EEMDC5TQAANFH5D77QM34ZTUKXPFGVL/
- https://security.gentoo.org/glsa/202401-33
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1831
- https://webkitgtk.org/security/WSA-2023-0009.html
- https://www.debian.org/security/2023/dsa-5527
