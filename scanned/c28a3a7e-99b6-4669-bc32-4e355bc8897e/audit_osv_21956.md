# [C] Allowing long password leads to denial of service in causefx/organizr

## Summary
Severity: Critical
Advisory: CVE-2022-1698
CVSS: 9.9 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:H)
Published: 2022-05-12
Source: https://osv.dev/vulnerability/CVE-2022-1698
Type: osv

## Details
Allowing long password leads to denial of service in GitHub repository causefx/organizr prior to 2.1.2000. This vulnerability can be abused by doing a DDoS attack for which genuine users will not able to access resources/applications.

## References
- https://huntr.dev/bounties/f4ab747b-e89a-4514-9432-ac1ea56639f3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1698.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1698
- https://github.com/causefx/organizr/commit/e4b4cff66c526f7b5bbaef0073c92c315c29bd56
