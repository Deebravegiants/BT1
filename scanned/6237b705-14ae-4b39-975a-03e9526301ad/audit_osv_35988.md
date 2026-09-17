# [H] Data::Entropy versions before 0.010 for Perl read remote entropy sources over plain HTTP

## Summary
Severity: High
Advisory: CVE-2026-18536
Aliases: GHSA-845w-rcqw-jwvv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-18536
Type: osv

## Details
Data::Entropy versions before 0.010 for Perl read remote entropy sources over plain HTTP.

The Data::Entropy::RawSource::RandomOrg and Data::Entropy::RawSource::RandomnumbersInfo remote sources are accessed over plain HTTP.

The Data::Entropy::RawSource::RandomOrg integrity check trivially matches any non-empty byte string.

Any on-path attacker, such as open WiFi, a compromised ISP, captive portal, or a hostile egress proxy substitutes the response and thereby chooses the bytes returned by rand_bits and rand_int for every application that selected one of these sources via with_entropy_source. The _checkbuf method response is equally attacker-controlled, so the retry/sleep behaviour is steerable too.

## References
- http://www.openwall.com/lists/oss-security/2026/08/01/8
- https://cpan.org/modules
- https://metacpan.org/release/RRWO/Data-Entropy-0.008/view/lib/Data/Entropy.pm#STATUS
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18536.json
- https://github.com/robrwo/Data-Entropy/security/advisories/GHSA-845w-rcqw-jwvv
- https://metacpan.org/release/RRWO/Data-Entropy-0.010/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-18536
- https://github.com/robrwo/Data-Entropy
- https://security.metacpan.org/docs/guides/random-data-for-security.html
