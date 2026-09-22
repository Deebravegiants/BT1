# [H] CVE-2021-4299

## Summary
Severity: High
Advisory: CVE-2021-4299
Aliases: GHSA-pfrm-4rjw-g9q5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-02
Source: https://osv.dev/vulnerability/CVE-2021-4299
Type: osv

## Details
A vulnerability classified as problematic was found in cronvel string-kit up to 0.12.7. This vulnerability affects the function naturalSort of the file lib/naturalSort.js. The manipulation leads to inefficient regular expression complexity. The attack can be initiated remotely. Upgrading to version 0.12.8 is able to address this issue. The name of the patch is 9cac4c298ee92c1695b0695951f1488884a7ca73. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-217180.

## References
- https://github.com/cronvel/string-kit/releases/tag/v0.12.8
- https://vuldb.com/?ctiid.217180
- https://vuldb.com/?id.217180
- https://github.com/cronvel/string-kit/commit/9cac4c298ee92c1695b0695951f1488884a7ca73
