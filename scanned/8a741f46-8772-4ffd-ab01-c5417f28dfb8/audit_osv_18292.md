# [H] CVE-2020-25829

## Summary
Severity: High
Advisory: CVE-2020-25829
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-16
Source: https://osv.dev/vulnerability/CVE-2020-25829
Type: osv

## Details
An issue has been found in PowerDNS Recursor before 4.1.18, 4.2.x before 4.2.5, and 4.3.x before 4.3.5. A remote attacker can cause the cached records for a given name to be updated to the Bogus DNSSEC validation state, instead of their actual DNSSEC Secure state, via a DNS ANY query. This results in a denial of service for installation that always validate (dnssec=validate), and for clients requesting validation when on-demand validation is enabled (dnssec=process).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00036.html
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-2020-07.html
- https://security.gentoo.org/glsa/202012-19
