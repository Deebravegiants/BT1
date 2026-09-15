# [H] Bytes::Random::Secure versions through 0.29 for Perl share internal state across forked processes

## Summary
Severity: High
Advisory: CVE-2026-11625
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-11625
Type: osv

## Details
Bytes::Random::Secure versions through 0.29 for Perl share internal state across forked processes.

When an object is initialised before forking, or when the functional interface is used, then the internal state for the PRNG is shared across processes and identical random streams will be produced.

Secrets generated in multiprocess applications are predictable across processes.

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2026-11702
- https://www.cve.org/CVERecord?id=CVE-2026-41564
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11625.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11625
- https://github.com/daoswald/Bytes-Random-Secure/issues/3
- https://github.com/daoswald/Bytes-Random-Secure/pull/4
- https://security.metacpan.org/patches/B/Bytes-Random-Secure/0.29/CVE-2026-11625-r1.patch
- https://github.com/daoswald/Bytes-Random-Secure
