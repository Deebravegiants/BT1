# [M] CVE-2018-1067

## Summary
Severity: Medium
Advisory: CVE-2018-1067
Aliases: GHSA-47mp-rq2x-wjf2
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2018-05-21
Source: https://osv.dev/vulnerability/CVE-2018-1067
Type: osv

## Details
In Undertow before versions 7.1.2.CR1, 7.1.2.GA it was found that the fix for CVE-2016-4993 was incomplete and Undertow web server is vulnerable to the injection of arbitrary HTTP headers, and also response splitting, due to insufficient sanitization and validation of user input before the input is used as part of an HTTP header value.

## References
- https://access.redhat.com/errata/RHSA-2018:1247
- https://access.redhat.com/errata/RHSA-2018:1248
- https://access.redhat.com/errata/RHSA-2018:1249
- https://access.redhat.com/errata/RHSA-2018:1251
- https://access.redhat.com/errata/RHSA-2018:2643
- https://access.redhat.com/errata/RHSA-2019:0877
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1067
