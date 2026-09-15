# [H] CVE-2024-23085

## Summary
Severity: High
Advisory: CVE-2024-23085
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-04-08
Source: https://osv.dev/vulnerability/CVE-2024-23085
Type: osv

## Details
Apfloat v1.10.1 was discovered to contain a NullPointerException via the component org.apfloat.internal.DoubleScramble::scramble(double[], int, int[]). NOTE: this is disputed by multiple third parties who believe there was not reasonable evidence to determine the existence of a vulnerability. The submission may have been based on a tool that is not sufficiently robust for vulnerability identification.

## References
- https://gist.github.com/LLM4IG/a4a54fc4abe044976a66af9fffedfc94
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23085.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-23085
- https://github.com/mtommila/apfloat
