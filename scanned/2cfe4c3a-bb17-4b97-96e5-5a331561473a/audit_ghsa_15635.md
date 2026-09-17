# [H] Local File Inclusion in Solara

## Summary
Severity: High
Advisory: GHSA-9794-pc4r-438w
CVE: CVE-2024-39903
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-07-12
Source: https://github.com/advisories/GHSA-9794-pc4r-438w
Type: github-advisory

## Affected
- PyPI: `solara` — affected >=0 <1.35.1

## Details
A Local File Inclusion (LFI) vulnerability was identified in widgetti/solara, in version <1.35.1, which was fixed in version 1.35.1. This vulnerability arises from the application's failure to properly validate URI fragments for directory traversal sequences such as '../' when serving static files. An attacker can exploit this flaw by manipulating the fragment part of the URI to read arbitrary files on the local file system. 

### References
- https://github.com/widgetti/solara/security/advisories/GHSA-9794-pc4r-438w
- https://github.com/widgetti/solara/commit/df2fd66a7f4e8ffd36e8678697a8a4f76760dc54
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-39903

## References
- https://github.com/widgetti/solara/security/advisories/GHSA-9794-pc4r-438w
- https://nvd.nist.gov/vuln/detail/CVE-2024-39903
- https://github.com/widgetti/solara/commit/df2fd66a7f4e8ffd36e8678697a8a4f76760dc54
- https://github.com/widgetti/solara
