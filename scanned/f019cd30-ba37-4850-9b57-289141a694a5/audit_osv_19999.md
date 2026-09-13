# [M] CVE-2021-29060

## Summary
Severity: Medium
Advisory: CVE-2021-29060
Aliases: GHSA-257v-vj4p-3w2h
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-06-21
Source: https://osv.dev/vulnerability/CVE-2021-29060
Type: osv

## Details
A Regular Expression Denial of Service (ReDOS) vulnerability was discovered in Color-String version 1.5.5 and below which occurs when the application is provided and checks a crafted invalid HWB string.

## References
- https://www.npmjs.com/package/color-string
- https://github.com/yetingli/SaveResults/blob/main/js/color-string.js
- https://github.com/Qix-/color-string/commit/0789e21284c33d89ebc4ab4ca6f759b9375ac9d3
- https://github.com/yetingli/PoCs/blob/main/CVE-2021-29060/Color-String.md
