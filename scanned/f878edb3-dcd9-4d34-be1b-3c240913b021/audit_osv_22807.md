# [H] nheko vulnerable to secret poisoning using MITM on secret requests by the homeserver

## Summary
Severity: High
Advisory: CVE-2022-39264
Aliases: GHSA-8jcp-8jq4-5mm7
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2022-09-28
Source: https://osv.dev/vulnerability/CVE-2022-39264
Type: osv

## Details
nheko is a desktop client for the Matrix communication application. All versions below 0.10.2 are vulnerable homeservers inserting malicious secrets, which could lead to man-in-the-middle attacks. Users can upgrade to version 0.10.2 to protect against this issue. As a workaround, one may apply the patch manually, avoid doing verifications of one's own devices, and/or avoid pressing the request button in the settings menu.

## References
- https://github.com/Nheko-Reborn/nheko/releases/tag/v0.10.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39264.json
- https://github.com/Nheko-Reborn/nheko/security/advisories/GHSA-8jcp-8jq4-5mm7
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TA6A5ADUVAYKD3ZFLF2JPZOTIOFJOEU7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YBOL6OOQGPZD2RLYT4EHAWTFXNIHLYEN/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39264
- https://github.com/Nheko-Reborn/nheko/commit/67bee15a389f9b8a9f6c3a340558d1e2319e7199
