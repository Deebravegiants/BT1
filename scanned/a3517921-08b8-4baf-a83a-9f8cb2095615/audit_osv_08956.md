# [H] CVE-2016-7069

## Summary
Severity: High
Advisory: CVE-2016-7069
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-11
Source: https://osv.dev/vulnerability/CVE-2016-7069
Type: osv

## Details
An issue has been found in dnsdist before 1.2.0 in the way EDNS0 OPT records are handled when parsing responses from a backend. When dnsdist is configured to add EDNS Client Subnet to a query, the response may contain an EDNS0 OPT record that has to be removed before forwarding the response to the initial client. On a 32-bit system, the pointer arithmetic used when parsing the received response to remove that record might trigger an undefined behavior leading to a crash.

## References
- http://www.securityfocus.com/bid/100509
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-7069
- https://dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2017-01.html
