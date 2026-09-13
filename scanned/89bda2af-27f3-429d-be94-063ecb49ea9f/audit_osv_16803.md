# [H] CVE-2019-9785

## Summary
Severity: High
Advisory: CVE-2019-9785
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-03-14
Source: https://osv.dev/vulnerability/CVE-2019-9785
Type: osv

## Details
gitnote 3.1.0 allows remote attackers to execute arbitrary code via a crafted Markdown file, as demonstrated by a javascript:window.parent.top.require('child_process').execFile substring in the onerror attribute of an IMG element.

## References
- https://github.com/CCCCCrash/POCs/tree/master/Web/gitnote
- https://github.com/zhaopengme/gitnote/issues/209
