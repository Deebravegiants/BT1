# [H] Missing connection timeout in Aardvark-dns

## Summary
Severity: High
Advisory: GHSA-g5jh-57wm-p79m
CVE: CVE-2024-8418
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-04
Source: https://github.com/advisories/GHSA-g5jh-57wm-p79m
Type: github-advisory

## Affected
- crates.io: `aardvark-dns` — affected >=1.12.0 <1.12.2

## Details
A flaw was found in Aardvark-dns versions 1.12.0 and 1.12.1. They contain a denial of service vulnerability due to serial processing of TCP DNS queries. This flaw allows a malicious client to keep a TCP connection open indefinitely, causing other DNS queries to time out and resulting in a denial of service for all other containers using aardvark-dns.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8418
- https://github.com/containers/aardvark-dns/issues/500
- https://github.com/containers/aardvark-dns/pull/503
- https://github.com/containers/aardvark-dns/commit/aa109bbd6743abd7027e589cc4b871dd2dce7d50
- https://access.redhat.com/errata/RHSA-2025:7094
- https://access.redhat.com/security/cve/CVE-2024-8418
- https://bugzilla.redhat.com/show_bug.cgi?id=2309683
- https://github.com/containers/aardvark-dns
