# [H] SSRF on /proxy in jgraph/drawio

## Summary
Severity: High
Advisory: CVE-2022-1713
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-05-16
Source: https://osv.dev/vulnerability/CVE-2022-1713
Type: osv

## Details
SSRF on /proxy in GitHub repository jgraph/drawio prior to 18.0.4. An attacker can make a request as the server and read its contents. This can lead to a leak of sensitive information.

## References
- https://huntr.dev/bounties/cad3902f-3afb-4ed2-abd0-9f96a248de11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1713.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1713
- https://github.com/jgraph/drawio/commit/283d41ec80ad410d68634245cf56114bc19331ee
