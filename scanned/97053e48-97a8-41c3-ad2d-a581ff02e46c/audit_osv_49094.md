# [H] CVE-2018-4200

## Summary
Severity: High
Advisory: CVE-2018-4200
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-08
Source: https://osv.dev/vulnerability/CVE-2018-4200
Type: osv

## Details
An issue was discovered in certain Apple products. iOS before 11.3.1 is affected. Safari before 11.1 is affected. iCloud before 7.5 on Windows is affected. iTunes before 12.7.5 on Windows is affected. tvOS before 11.4 is affected. The issue involves the "WebKit" component. It allows remote attackers to execute arbitrary code or cause a denial of service (memory corruption and application crash) via a crafted web site that triggers a WebCore::jsElementScrollHeightGetter use-after-free.

## References
- http://www.securityfocus.com/bid/103961
- http://www.securitytracker.com/id/1040743
- https://support.apple.com/HT208852
- https://support.apple.com/HT208853
- https://security.gentoo.org/glsa/201808-04
- https://support.apple.com/HT208741
- https://support.apple.com/HT208743
- https://support.apple.com/HT208850
- https://usn.ubuntu.com/3640-1/
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1525
- https://www.exploit-db.com/exploits/44566/
