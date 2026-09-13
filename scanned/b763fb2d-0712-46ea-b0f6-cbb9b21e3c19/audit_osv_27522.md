# [C] CVE-2024-23086

## Summary
Severity: Critical
Advisory: CVE-2024-23086
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-08
Source: https://osv.dev/vulnerability/CVE-2024-23086
Type: osv

## Details
Apfloat v1.10.1 was discovered to contain a stack overflow via the component org.apfloat.internal.DoubleModMath::modPow(double. NOTE: this is disputed by multiple third parties who believe there was not reasonable evidence to determine the existence of a vulnerability. The submission may have been based on a tool that is not sufficiently robust for vulnerability identification.

## References
- https://gist.github.com/LLM4IG/63ad1a4d1e3955043b7a90fdbf36676b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23086.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-23086
- https://github.com/mtommila/apfloat
