# [M] Lollms vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-cm59-8rmv-f2cj
CVE: CVE-2024-6581
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-10-29
Source: https://github.com/advisories/GHSA-cm59-8rmv-f2cj
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=0

## Details
A vulnerability in the discussion image upload function of the Lollms application, version v9.9, allows for the uploading of SVG files. Due to incomplete filtering in the sanitize_svg function, this can lead to cross-site scripting (XSS) vulnerabilities, which in turn pose a risk of remote code execution. The sanitize_svg function only removes script elements and 'on*' event attributes, but does not account for other potential vectors for XSS within SVG files. This vulnerability can be exploited when authorized users access a malicious URL containing the crafted SVG file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6581
- https://github.com/parisneo/lollms/commit/328b960a0de2097e13654ac752253e9541521ddd
- https://github.com/parisneo/lollms
- https://github.com/pypa/advisory-database/tree/main/vulns/lollms/PYSEC-2024-116.yaml
- https://huntr.com/bounties/ad68ecd6-44e2-449b-8e7e-f2b71b1b43c7
