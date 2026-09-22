# [M] CVE-2017-16137

## Summary
Severity: Medium
Advisory: CVE-2017-16137
Aliases: GHSA-gxpj-cx7g-858c
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2018-06-07
Source: https://osv.dev/vulnerability/CVE-2017-16137
Type: osv

## Details
The debug module is vulnerable to regular expression denial of service when untrusted user input is passed into the o formatter. It takes around 50k characters to block for 2 seconds making this a low severity issue.

## References
- https://lists.apache.org/thread.html/r8ba4c628fba7181af58817d452119481adce4ba92e889c643e4c7dd3%40%3Ccommits.netbeans.apache.org%3E
- https://lists.apache.org/thread.html/rb5ac16fad337d1f3bb7079549f97d8166d0ef3082629417c39f12d63%40%3Cnotifications.netbeans.apache.org%3E
- https://github.com/visionmedia/debug/issues/501
- https://nodesecurity.io/advisories/534
- https://github.com/visionmedia/debug/pull/504
