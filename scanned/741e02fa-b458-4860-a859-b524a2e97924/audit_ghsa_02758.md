# [H] Incorrect Regular Expression in RestSharp

## Summary
Severity: High
Advisory: GHSA-9pq7-rcxv-47vq
CVE: CVE-2021-27293
CWE: CWE-185, CWE-697
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-07-14
Source: https://github.com/advisories/GHSA-9pq7-rcxv-47vq
Type: github-advisory

## Affected
- NuGet: `RestSharp` — affected >=0 <106.11.8-alpha.0.13

## Details
RestSharp < 106.11.8-alpha.0.13 uses a regular expression which is vulnerable to Regular Expression Denial of Service (ReDoS) when converting strings into DateTimes. If a server responds with a malicious string, the client using RestSharp will be stuck processing it for an exceedingly long time. Thus the remote server can trigger Denial of Service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27293
- https://github.com/restsharp/RestSharp/issues/1556
- https://github.com/restsharp/RestSharp/commit/be39346784b68048b230790d15333574341143bc
- https://restsharp.dev
