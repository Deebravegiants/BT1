# [H] CVE-2020-8595

## Summary
Severity: High
Advisory: CVE-2020-8595
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2020-8595
Type: osv

## Details
Istio versions 1.2.10 (End of Life) and prior, 1.3 through 1.3.7, and 1.4 through 1.4.3 allows authentication bypass. The Authentication Policy exact-path matching logic can allow unauthorized access to HTTP paths even if they are configured to be only accessed after presenting a valid JWT token. For example, an attacker can add a ? or # character to a URI that would otherwise satisfy an exact-path match.

## References
- https://access.redhat.com/errata/RHSA-2020:0477
- https://access.redhat.com/security/cve/cve-2020-8595
- https://istio.io/news/security/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-8595
- https://github.com/istio/istio/commits/master
- https://istio.io/news/security/istio-security-2020-001/
