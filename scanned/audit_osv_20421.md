# [M] CVE-2021-33510

## Summary
Severity: Medium
Advisory: CVE-2021-33510
Aliases: GHSA-4mg4-wvmx-5332, PYSEC-2021-82
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-05-21
Source: https://osv.dev/vulnerability/CVE-2021-33510
Type: osv

## Details
Plone through 5.2.4 allows remote authenticated managers to conduct SSRF attacks via an event ical URL, to read one line of a file.

## References
- http://www.openwall.com/lists/oss-security/2021/05/22/1
- https://plone.org/security/hotfix/20210518/server-side-request-forgery-via-event-ical-url
