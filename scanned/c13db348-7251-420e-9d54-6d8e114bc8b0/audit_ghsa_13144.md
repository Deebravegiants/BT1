# [H] Electron affected by libvpx's heap buffer overflow in vp8 encoding

## Summary
Severity: High
Advisory: GHSA-qqvq-6xgj-jw8g
CVE: CVE-2023-5217
CWE: CWE-787
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-28
Source: https://github.com/advisories/GHSA-qqvq-6xgj-jw8g
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <22.3.25
- npm: `electron` — affected >=24.0.0 <24.8.5
- npm: `electron` — affected >=25.0.0 <25.8.4
- npm: `electron` — affected >=26.0.0 <26.2.4
- npm: `electron` — affected >=27.0.0-alpha.1 <27.0.0-beta.8

## Details
Heap buffer overflow in vp8 encoding in libvpx in Google Chrome prior to 117.0.5938.132 and libvpx 1.13.1 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5217
- https://github.com/electron/electron/pull/40022
- https://github.com/electron/electron/pull/40023
- https://github.com/electron/electron/pull/40024
- https://github.com/electron/electron/pull/40025
- https://github.com/electron/electron/pull/40026
- https://github.com/webmproject/libvpx/commit/af6dedd715f4307669366944cca6e0417b290282
- https://github.com/webmproject/libvpx/commit/3fbd1dca6a4d2dad332a2110d646e4ffef36d590
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BCVSHVX2RFBU3RMCUFSATVQEJUFD4Q63
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CWEJYS5NC7KVFYU3OAMPKQDYN6JQGVK6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TE7F54W5O5RS4ZMAAC7YK3CZWQXIDSKB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WTRUIS3564P7ZLM2S2IH4Y4KZ327LI4I
- https://pastebin.com/TdkC4pDv
- https://security-tracker.debian.org/tracker/CVE-2023-5217
- https://security.gentoo.org/glsa/202310-04
- https://security.gentoo.org/glsa/202401-34
- https://stackdiary.com/google-discloses-a-webm-vp8-bug-tracked-as-cve-2023-5217
- https://support.apple.com/kb/HT213961
- https://support.apple.com/kb/HT213972
- https://twitter.com/maddiestone/status/1707163313711497266
