# [C] CVE-2017-1001002

## Summary
Severity: Critical
Advisory: CVE-2017-1001002
Aliases: GHSA-vx5c-87qx-cv6c
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-27
Source: https://osv.dev/vulnerability/CVE-2017-1001002
Type: osv

## Details
math.js before 3.17.0 had an arbitrary code execution in the JavaScript engine. Creating a typed function with JavaScript code in the name could result arbitrary execution.

## References
- https://github.com/josdejong/mathjs/blob/master/HISTORY.md#2017-11-18-version-3170
- https://github.com/josdejong/mathjs/commit/8d2d48d81b3c233fb64eb2ec1d7a9e1cf6a55a90
