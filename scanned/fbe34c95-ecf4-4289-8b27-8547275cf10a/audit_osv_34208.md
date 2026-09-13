# [C] UnoPim vulnerable to remote code execution through Arbitrary File upload

## Summary
Severity: Critical
Advisory: CVE-2025-55743
Aliases: GHSA-v22v-xwh7-2vrm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-08-21
Source: https://osv.dev/vulnerability/CVE-2025-55743
Type: osv

## Details
UnoPim is an open-source Product Information Management (PIM) system built on the Laravel framework. Before 0.2.1, the image upload at the user creation feature performs only client side file type validation. A user can capture the request by uploading an image, capture the request through a Proxy like Burp suite. Make changes to the file extension and content. The vulnerability is fixed in 0.2.1.

## References
- https://drive.proton.me/urls/PH1ESMKHMW#4Vxb2KNu3tmn
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55743.json
- https://github.com/unopim/unopim/security/advisories/GHSA-v22v-xwh7-2vrm
- https://nvd.nist.gov/vuln/detail/CVE-2025-55743
