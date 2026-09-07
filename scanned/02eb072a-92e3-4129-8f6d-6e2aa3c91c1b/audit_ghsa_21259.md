# [H] Heartex - Label Studio Community Edition vulnerable to SSRF in the Data Import module

## Summary
Severity: High
Advisory: GHSA-pc6f-259w-w3j6
CVE: CVE-2022-36551
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-10-04
Source: https://github.com/advisories/GHSA-pc6f-259w-w3j6
Type: github-advisory

## Affected
- PyPI: `label-studio` — affected >=0 <1.6.0

## Details
A Server Side Request Forgery (SSRF) in the Data Import module in Heartex - Label Studio Community Edition versions 1.5.0 and earlier allows an authenticated user to access arbitrary files on the system. Furthermore, self-registration is enabled by default in these versions of Label Studio enabling a remote attacker to create a new account and then exploit the SSRF. This issue is fixed in version 1.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36551
- https://github.com/heartexlabs/label-studio/pull/2840
- https://github.com/heartexlabs/label-studio/commit/501142cb815ac964b0c600c491885b67386870c2
- https://github.com/heartexlabs/label-studio
- https://github.com/heartexlabs/label-studio/releases/tag/1.6.0
- https://github.com/pypa/advisory-database/tree/main/vulns/label-studio/PYSEC-2022-300.yaml
- http://heartex.com
- http://labelstud.io
- http://packetstormsecurity.com/files/171548/Label-Studio-1.5.0-Server-Side-Request-Forgery.html
