# [M] Nokogiri XSLT transform has a memory leak

## Summary
Severity: Medium
Advisory: GHSA-v2fc-qm4h-8hqv
CVE: CVE-2026-79771
CWE: CWE-401
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-v2fc-qm4h-8hqv
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.19.3

## Details
## Summary

Nokogiri's `Nokogiri::XSLT::Stylesheet#transform` leaks a small heap allocation when passed a Ruby string parameter containing a null byte.

For applications that pass attacker-controlled input through `XSLT.transform` parameters, this may be a vector for a denial of service attack against long-running processes.


## Mitigation

Upgrade to Nokogiri `>= 1.19.3`.

Users may also be able to mitigate this issue without upgrading by validating untrusted transform parameters before passing them to `Nokogiri::XSLT::Stylesheet#transform`.


## Severity

The Nokogiri maintainers have evaluated this as **Moderate Severity**, CVSS 5.3.

Each leaked allocation is approximately 24–32 bytes, so meaningful memory growth requires sustained attacker-controlled traffic at high call rates. The bug does not cause memory corruption, information disclosure, or any change in the behavior of the transform itself, and the string-handling exception is raised as expected.

Applications that do not pass raw attacker-controlled bytes to XSLT parameters are unlikely to be affected in practice.


## Resources

- [CWE-401: Missing Release of Memory after Effective Lifetime](https://cwe.mitre.org/data/definitions/401.html)


## Credit

This vulnerability was responsibly reported by @Captainjack-kor.

## References
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-v2fc-qm4h-8hqv
- https://nvd.nist.gov/vuln/detail/CVE-2026-79771
- https://github.com/sparklemotion/nokogiri
- https://www.vulncheck.com/advisories/nokogiri-before-memory-leak-via-xslt-transform
