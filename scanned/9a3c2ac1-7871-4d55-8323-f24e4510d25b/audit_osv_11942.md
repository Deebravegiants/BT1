# [M] CVE-2018-1000154

## Summary
Severity: Medium
Advisory: CVE-2018-1000154
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2018-04-05
Source: https://osv.dev/vulnerability/CVE-2018-1000154
Type: osv

## Details
Zammad GmbH Zammad version 2.3.0 and earlier contains a Improper Neutralization of Script-Related HTML Tags in a Web Page (CWE-80) vulnerability in the subject of emails which are not html quoted in certain cases. This can result in the embedding and execution of java script code on users browser. This attack appear to be exploitable via the victim openning a ticket. This vulnerability appears to have been fixed in 2.3.1, 2.2.2 and 2.1.3.

## References
- https://github.com/zammad/zammad/issues/1869
- https://zammad.com/news/release-2-4
- https://zammad.com/news/security-advisory-zaa-2018-01
