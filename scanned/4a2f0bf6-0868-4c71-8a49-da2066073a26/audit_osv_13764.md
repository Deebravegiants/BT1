# [H] CVE-2018-25110

## Summary
Severity: High
Advisory: CVE-2018-25110
Aliases: GHSA-p9wx-2529-fp83
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-23
Source: https://osv.dev/vulnerability/CVE-2018-25110
Type: osv

## Details
Marked prior to version 0.3.17 is vulnerable to a Regular Expression Denial of Service (ReDoS) attack due to catastrophic backtracking in several regular expressions used for parsing HTML tags and markdown links. An attacker can exploit this vulnerability by providing specially crafted markdown input, such as deeply nested or repetitively structured brackets or tag attributes, which cause the parser to hang and lead to a Denial of Service.

## References
- https://github.com/markedjs/marked/issues/1070
- https://github.com/markedjs/marked/commit/20bfc106013ed45713a21672ad4a34df94dcd485
- https://github.com/markedjs/marked/pull/1083
- https://github.com/Checkmarx/Vulnerabilities-Proofs-of-Concept/tree/main/2018/CVE-2018-25110
