# [M] CVE-2017-2609

## Summary
Severity: Medium
Advisory: CVE-2017-2609
Aliases: GHSA-v222-w2mw-xjc6
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2017-2609
Type: osv

## Details
jenkins before versions 2.44, 2.32.2 is vulnerable to an information disclosure vulnerability in search suggestions (SECURITY-385). The autocomplete feature on the search box discloses the names of the views in its suggestions, including the ones for which the current user does not have access to.

## References
- http://www.securityfocus.com/bid/95964
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2609
- https://github.com/jenkinsci/jenkins/commit/13905d8224899ba7332fe9af4e330ea96a2ae319
