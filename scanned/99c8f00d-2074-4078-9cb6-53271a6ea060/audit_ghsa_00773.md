# [M] Feedgen Vulnerable to XML Denial of Service Attacks

## Summary
Severity: Medium
Advisory: GHSA-g8q7-xv52-hf9f
CVE: CVE-2020-5227
CWE: CWE-776
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-01-28
Source: https://github.com/advisories/GHSA-g8q7-xv52-hf9f
Type: github-advisory

## Affected
- PyPI: `feedgen` — affected >=0 <0.9.0

## Details
### Impact

The *feedgen* library allows supplying XML as content for some of the available fields. This XML will be parsed and integrated into the existing XML tree. During this process, feedgen is vulnerable to [XML Denial of Service Attacks](https://docs.microsoft.com/en-us/archive/msdn-magazine/2009/november/xml-denial-of-service-attacks-and-defenses) (e.g. XML Bomb).

This becomes a concern in particular if feedgen is used to include content from untrused sources and if XML (including XHTML) is directly included instead of providing plain tex content only.

### Patches

This problem has been fixed in feedgen 0.9.0 which disallows XML entity expansion and external resources.

### Workarounds

Updating is strongly recommended and should not be problematic. Nevertheless, as a workaround, avoid providing XML directly to feedgen or ensure that no entity expansion is part of the XML. 

### References

- [Security Briefs - XML Denial of Service Attacks and Defenses](https://docs.microsoft.com/en-us/archive/msdn-magazine/2009/november/xml-denial-of-service-attacks-and-defenses)
- [Billion laughs attack](https://en.wikipedia.org/wiki/Billion_laughs_attack#cite_note-2)

### For more information

If you have any questions or comments about this advisory:
- Open an issue in [lkiesow/python-feedgen](https://github.com/lkiesow/python-feedgen/issues)
- Send an email to security@lkiesow.de

## References
- https://github.com/lkiesow/python-feedgen/security/advisories/GHSA-g8q7-xv52-hf9f
- https://nvd.nist.gov/vuln/detail/CVE-2020-5227
- https://github.com/lkiesow/python-feedgen/commit/f57a01b20fa4aaaeccfa417f28e66b4084b9d0cf
- https://docs.microsoft.com/en-us/archive/msdn-magazine/2009/november/xml-denial-of-service-attacks-and-defenses
- https://github.com/lkiesow/python-feedgen
- https://github.com/pypa/advisory-database/tree/main/vulns/feedgen/PYSEC-2020-231.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T6I5ENUYGFNMIH6ZQ62FZ6VU2WD3SIOI
