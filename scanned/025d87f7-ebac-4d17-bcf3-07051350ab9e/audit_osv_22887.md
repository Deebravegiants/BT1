# [M] CVE-2022-40276

## Summary
Severity: Medium
Advisory: CVE-2022-40276
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-11-03
Source: https://osv.dev/vulnerability/CVE-2022-40276
Type: osv

## Details
Zettlr version 2.3.0 allows an external attacker to remotely obtain arbitrary local files on any client that attempts to view a malicious markdown file through Zettlr. This is possible because the application does not have a CSP policy (or at least not strict enough) and/or does not properly validate the contents of markdown files before rendering them.

## References
- https://fluidattacks.com/advisories/avicii/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40276.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-40276
- https://github.com/Zettlr/Zettlr
