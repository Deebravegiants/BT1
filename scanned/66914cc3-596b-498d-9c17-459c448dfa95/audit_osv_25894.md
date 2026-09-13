# [H] Squid: denial of service in http digest authentication

## Summary
Severity: High
Advisory: CVE-2023-46847
Aliases: GHSA-phqj-m8gv-cq4g
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2023-46847
Type: osv

## Details
Squid is vulnerable to a Denial of Service,  where a remote attacker can perform buffer overflow attack by writing up to 2 MB of arbitrary data to heap memory when Squid is configured to accept HTTP Digest Authentication.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/01/msg00003.html
- https://access.redhat.com/errata/RHSA-2023:6266
- https://access.redhat.com/errata/RHSA-2023:6267
- https://access.redhat.com/errata/RHSA-2023:6268
- https://access.redhat.com/errata/RHSA-2023:6748
- https://access.redhat.com/errata/RHSA-2023:6801
- https://access.redhat.com/errata/RHSA-2023:6803
- https://access.redhat.com/errata/RHSA-2023:6804
- https://access.redhat.com/errata/RHSA-2023:6805
- https://access.redhat.com/errata/RHSA-2023:6810
- https://access.redhat.com/errata/RHSA-2023:6882
- https://access.redhat.com/errata/RHSA-2023:6884
- https://access.redhat.com/errata/RHSA-2023:7213
- https://access.redhat.com/errata/RHSA-2023:7576
- https://access.redhat.com/errata/RHSA-2023:7578
- https://access.redhat.com/security/cve/CVE-2023-46847
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46847.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-phqj-m8gv-cq4g
- https://nvd.nist.gov/vuln/detail/CVE-2023-46847
