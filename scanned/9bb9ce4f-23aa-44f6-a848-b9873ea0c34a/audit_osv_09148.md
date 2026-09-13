# [M] CVE-2016-8627

## Summary
Severity: Medium
Advisory: CVE-2016-8627
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-11
Source: https://osv.dev/vulnerability/CVE-2016-8627
Type: osv

## Details
admin-cli before versions 3.0.0.alpha25, 2.2.1.cr2 is vulnerable to an EAP feature to download server log files that allows logs to be available via GET requests making them vulnerable to cross-origin attacks. An attacker could trigger the user's browser to request the log files consuming enough resources that normal server functioning could be impaired.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0170.html
- http://rhn.redhat.com/errata/RHSA-2017-0171.html
- http://rhn.redhat.com/errata/RHSA-2017-0172.html
- http://rhn.redhat.com/errata/RHSA-2017-0173.html
- http://rhn.redhat.com/errata/RHSA-2017-0244.html
- http://rhn.redhat.com/errata/RHSA-2017-0245.html
- http://rhn.redhat.com/errata/RHSA-2017-0246.html
- http://rhn.redhat.com/errata/RHSA-2017-0247.html
- http://rhn.redhat.com/errata/RHSA-2017-0250.html
- http://www.securityfocus.com/bid/95698
- http://www.securitytracker.com/id/1037660
- https://access.redhat.com/errata/RHSA-2017:3454
- https://access.redhat.com/errata/RHSA-2017:3455
- https://access.redhat.com/errata/RHSA-2017:3456
- https://access.redhat.com/errata/RHSA-2017:3458
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-8627
