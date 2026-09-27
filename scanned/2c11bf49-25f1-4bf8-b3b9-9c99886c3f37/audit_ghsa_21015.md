# [H] rdiffweb vulnerable to potential DoS via memory consumption

## Summary
Severity: High
Advisory: GHSA-xhw9-4wqq-x67v
CVE: CVE-2022-3298
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-27
Source: https://github.com/advisories/GHSA-xhw9-4wqq-x67v
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.4.8

## Details
rdiffweb prior to 2.4.8 is vulnerable to a potential Dos attack via an unlimited length "title" field when adding an SSH key.
This can result in excess memory consumption, leading to a Denial of Service (DoS). This issue is patched in version 2.4.8. There are no known workarounds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3298
- https://github.com/ikus060/rdiffweb/commit/626cca1b75b6c587afd4241a9692e8929b1921a5
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-294.yaml
- https://huntr.dev/bounties/f9fedf94-41c9-49c4-8552-e407123a44e7
