# [C] Squid: request/response smuggling in http/1.1 and icap

## Summary
Severity: Critical
Advisory: CVE-2023-46846
Aliases: GHSA-j83v-w3p4-5cqh
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2023-46846
Type: osv

## Details
SQUID is vulnerable to HTTP request smuggling, caused by chunked decoder lenience, allows a remote attacker to perform Request/Response smuggling past firewall and frontend security systems.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/01/msg00003.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00008.html
- https://access.redhat.com/errata/RHSA-2023:6266
- https://access.redhat.com/errata/RHSA-2023:6267
- https://access.redhat.com/errata/RHSA-2023:6268
- https://access.redhat.com/errata/RHSA-2023:6748
- https://access.redhat.com/errata/RHSA-2023:6801
- https://access.redhat.com/errata/RHSA-2023:6803
- https://access.redhat.com/errata/RHSA-2023:6804
- https://access.redhat.com/errata/RHSA-2023:6810
- https://access.redhat.com/errata/RHSA-2023:7213
- https://access.redhat.com/errata/RHSA-2024:11049
- https://access.redhat.com/security/cve/CVE-2023-46846
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46846.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-j83v-w3p4-5cqh
- https://nvd.nist.gov/vuln/detail/CVE-2023-46846
- https://security.netapp.com/advisory/ntap-20231130-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2245910
- https://github.com/squid-cache/squid
