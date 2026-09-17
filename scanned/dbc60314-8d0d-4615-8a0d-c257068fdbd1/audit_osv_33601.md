# [C] CVE-2025-47154

## Summary
Severity: Critical
Advisory: CVE-2025-47154
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-47154
Type: osv

## Details
LibJS in Ladybird before f5a6704 mishandles the freeing of the vector that arguments_list references, leading to a use-after-free, and allowing remote attackers to execute arbitrary code via a crafted .js file. NOTE: the GitHub README says "Ladybird is in a pre-alpha state, and only suitable for use by developers."

## References
- https://news.ycombinator.com/item?id=43852096
- https://jessie.cafe/posts/pwning-ladybirds-libjs/
- https://github.com/LadybirdBrowser/ladybird/commit/f5a670421954fc7130c3685b713c621b29516669
