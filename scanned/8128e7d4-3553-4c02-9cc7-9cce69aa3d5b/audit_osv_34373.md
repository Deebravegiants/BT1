# [H] Python-kdcproxy: unauthenticated ssrf via realm‑controlled dns srv

## Summary
Severity: High
Advisory: CVE-2025-59088
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-59088
Type: osv

## Details
If kdcproxy receives a request for a realm which does not have server addresses defined in its configuration, by default, it will query SRV records in the DNS zone matching the requested realm name. This creates a server-side request forgery vulnerability, since an attacker could send a request for a realm matching a DNS zone where they created SRV records pointing to arbitrary ports and hostnames (which may resolve to loopback or internal IP addresses). This vulnerability can be exploited to probe internal network topology and firewall rules, perform port scanning, and exfiltrate data. Deployments where
the "use_dns" setting is explicitly set to false are not affected.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:21138
- https://access.redhat.com/errata/RHSA-2025:21139
- https://access.redhat.com/errata/RHSA-2025:21140
- https://access.redhat.com/errata/RHSA-2025:21141
- https://access.redhat.com/errata/RHSA-2025:21142
- https://access.redhat.com/errata/RHSA-2025:21448
- https://access.redhat.com/errata/RHSA-2025:21748
- https://access.redhat.com/errata/RHSA-2025:21806
- https://access.redhat.com/errata/RHSA-2025:21818
- https://access.redhat.com/errata/RHSA-2025:21819
- https://access.redhat.com/errata/RHSA-2025:21820
- https://access.redhat.com/errata/RHSA-2025:21821
- https://access.redhat.com/errata/RHSA-2025:22982
- https://access.redhat.com/security/cve/CVE-2025-59088
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59088.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59088
- https://bugzilla.redhat.com/show_bug.cgi?id=2393955
- https://github.com/latchset/kdcproxy/pull/68
- https://github.com/latchset/kdcproxy
