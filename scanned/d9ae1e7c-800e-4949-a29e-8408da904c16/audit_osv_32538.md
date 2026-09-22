# [H] CVE-2025-32111

## Summary
Severity: High
Advisory: CVE-2025-32111
CVSS: 8.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-04-04
Source: https://osv.dev/vulnerability/CVE-2025-32111
Type: osv

## Details
The Docker image from acme.sh before 40b6db6 is based on a .github/workflows/dockerhub.yml file that lacks "persist-credentials: false" for actions/checkout.

## References
- https://github.com/actions/checkout/blob/85e6279cec87321a52edac9c87bce653a07cf6c2/README.md?plain=1#L70-L72
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32111.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32111
- https://github.com/acmesh-official/acme.sh/commit/40b6db6a2715628aa977ed1853fe5256704010ae
- https://github.com/acmesh-official/acme.sh/commit/a1de13657e79c5471dbc8fa3539ea39160937389
