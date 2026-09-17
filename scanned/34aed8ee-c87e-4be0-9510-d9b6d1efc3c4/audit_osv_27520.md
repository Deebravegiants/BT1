# [H] CVE-2024-23084

## Summary
Severity: High
Advisory: CVE-2024-23084
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-08
Source: https://osv.dev/vulnerability/CVE-2024-23084
Type: osv

## Details
Apfloat v1.10.1 was discovered to contain an ArrayIndexOutOfBoundsException via the component org.apfloat.internal.DoubleCRTMath::add(double[], double[]). NOTE: this is disputed by multiple third parties who believe there was not reasonable evidence to determine the existence of a vulnerability. The submission may have been based on a tool that is not sufficiently robust for vulnerability identification.

## References
- https://gist.github.com/LLM4IG/5b7dd0a87db14d9c95d4c0ea62e0195b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23084.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-23084
- https://github.com/mtommila/apfloat
