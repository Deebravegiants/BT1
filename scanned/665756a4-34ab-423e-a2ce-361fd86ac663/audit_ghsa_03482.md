# [H] Regular Expression Denial of Service (ReDoS)

## Summary
Severity: High
Advisory: GHSA-vx3p-948g-6vhq
CVE: CVE-2021-27290
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-03-19
Source: https://github.com/advisories/GHSA-vx3p-948g-6vhq
Type: github-advisory

## Affected
- npm: `ssri` — affected >=5.2.2 <6.0.2
- npm: `ssri` — affected >=7.0.0 <7.1.1
- npm: `ssri` — affected >=8.0.0 <8.0.1

## Details
npm `ssri` 5.2.2-6.0.1 and 7.0.0-8.0.0, processes SRIs using a regular expression which is vulnerable to a denial of service. Malicious SRIs could take an extremely long time to process, leading to denial of service. This issue only affects consumers using the strict option.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27290
- https://github.com/npm/ssri/pull/20#issuecomment-842677644
- https://github.com/npm/ssri/commit/76e223317d971f19e4db8191865bdad5edee40d2
- https://github.com/npm/ssri/commit/809c84d09ea87c3857fa171d42914586899d4538
- https://github.com/npm/ssri/commit/b30dfdb00bb94ddc49a25a85a18fb27afafdfbb1
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://doyensec.com/resources/Doyensec_Advisory_ssri_redos.pdf
- https://github.com/npm/ssri
- https://github.com/yetingli/SaveResults/blob/main/pdf/ssri-redos.pdf
- https://npmjs.com
- https://www.npmjs.com/package/ssri
- https://www.oracle.com/security-alerts/cpuoct2021.html
