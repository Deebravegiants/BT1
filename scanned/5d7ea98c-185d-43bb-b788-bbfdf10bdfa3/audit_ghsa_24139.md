# [H] Red Hat Wildfly DoS

## Summary
Severity: High
Advisory: GHSA-p4xg-cpr9-vwvj
CVE: CVE-2016-9589
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p4xg-cpr9-vwvj
Type: github-advisory

## Affected
- Maven: `org.wildfly:wildfly-undertow` — affected >=0 <11.0.0.Beta1

## Details
Undertow in Red Hat wildfly before version 11.0.0.Beta1 is vulnerable to a resource exhaustion resulting in a denial of service. Undertow keeps a cache of seen HTTP headers in persistent connections. It was found that this cache can easily exploited to fill memory with garbage, up to "max-headers" (default 200) * "max-header-size" (default 1MB) per active TCP connection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9589
- https://access.redhat.com/errata/RHSA-2017:0872
- https://access.redhat.com/errata/RHSA-2017:0873
- https://access.redhat.com/errata/RHSA-2017:3454
- https://access.redhat.com/errata/RHSA-2017:3455
- https://access.redhat.com/errata/RHSA-2017:3456
- https://access.redhat.com/errata/RHSA-2017:3458
- https://bugzilla.redhat.com/show_bug.cgi?id=1404782
- https://github.com/wildfly/wildfly
- https://web.archive.org/web/20200227180917/https://www.securityfocus.com/bid/97060
- http://rhn.redhat.com/errata/RHSA-2017-0830.html
- http://rhn.redhat.com/errata/RHSA-2017-0831.html
- http://rhn.redhat.com/errata/RHSA-2017-0832.html
- http://rhn.redhat.com/errata/RHSA-2017-0834.html
- http://rhn.redhat.com/errata/RHSA-2017-0876.html
