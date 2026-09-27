# [H] CVE-2022-2157

## Summary
Severity: High
Advisory: CVE-2022-2157
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-07-28
Source: https://osv.dev/vulnerability/CVE-2022-2157
Type: osv

## Details
Use after free in Interest groups in Google Chrome prior to 103.0.5060.53 allowed a remote attacker who had compromised the renderer process to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5BQRTR4SIUNIHLLPWTGYSDNQK7DYCRSB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H2C4XOJVIILDXTOSMWJXHSQNEXFWSOD7/
- https://security.gentoo.org/glsa/202208-25
- https://chromereleases.googleblog.com/2022/06/stable-channel-update-for-desktop_21.html
- https://crbug.com/1327312
