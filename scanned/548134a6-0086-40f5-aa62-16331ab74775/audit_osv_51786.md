# [H] CVE-2021-4057

## Summary
Severity: High
Advisory: CVE-2021-4057
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-12-23
Source: https://osv.dev/vulnerability/CVE-2021-4057
Type: osv

## Details
Use after free in file API in Google Chrome prior to 96.0.4664.93 allowed a remote attacker who had compromised the renderer process to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3W46HRT2UVHWSLZB6JZHQF6JNQWKV744/
- http://packetstormsecurity.com/files/165486/Chrome-storage-BlobURLStoreImpl-Revoke-Heap-Use-After-Free.html
- https://chromereleases.googleblog.com/2021/12/stable-channel-update-for-desktop.html
- https://security.gentoo.org/glsa/202208-25
- https://www.debian.org/security/2022/dsa-5046
- https://crbug.com/1262183
