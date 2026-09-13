# [H] DataEase has a vulnerability to obtain user cookies

## Summary
Severity: High
Advisory: CVE-2023-40183
Aliases: GHSA-w2r4-2r4w-fjxv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-09-21
Source: https://osv.dev/vulnerability/CVE-2023-40183
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to version 1.18.11, DataEase has a vulnerability that allows an attacker to to obtain user cookies. The program only uses the `ImageIO.read()` method to determine whether the file is an image file or not. There is no whitelisting restriction on file suffixes. This allows the attacker to synthesize the attack code into an image for uploading and change the file extension to html. The attacker may steal user cookies by accessing links. The vulnerability has been fixed in v1.18.11. There are no known workarounds.

## References
- https://github.com/dataease/dataease/releases/tag/v1.18.11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40183.json
- https://github.com/dataease/dataease/security/advisories/GHSA-w2r4-2r4w-fjxv
- https://nvd.nist.gov/vuln/detail/CVE-2023-40183
- https://github.com/dataease/dataease/commit/826513053146721a2b3e09a9c9d3ea41f8f10569
