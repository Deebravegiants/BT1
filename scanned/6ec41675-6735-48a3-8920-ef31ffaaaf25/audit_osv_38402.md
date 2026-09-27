# [M] Kamailio Auth: Processing Vulnerability For Additional Authenticated User Identity Checks

## Summary
Severity: Medium
Advisory: CVE-2026-39864
Aliases: GHSA-6m86-m342-g48m
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-39864
Type: osv

## Details
Kamailio is an open source implementation of a SIP Signaling Server. Prior to 6.0.5 and 5.8.7, an out-of-bounds read in the auth module of Kamailio (formerly OpenSER and SER) allows remote attackers to cause a denial of service (process crash) via a specially crafted SIP packet if a successful user authentication without a database backend is followed by additional user identity checks. This vulnerability is fixed in 6.0.5 and 5.8.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39864.json
- https://github.com/kamailio/kamailio/security/advisories/GHSA-6m86-m342-g48m
- https://nvd.nist.gov/vuln/detail/CVE-2026-39864
