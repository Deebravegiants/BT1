# [M] CVE-2023-34041-Abuse of HTTP Hop-by-Hop Headers in Cloud Foundry Gorouter

## Summary
Severity: Medium
Advisory: CVE-2023-34041
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-09-08
Source: https://osv.dev/vulnerability/CVE-2023-34041
Type: osv

## Details
Cloud foundry routing release versions prior to 0.278.0 are vulnerable to abuse of HTTP Hop-by-Hop Headers. An unauthenticated attacker can use this vulnerability for headers like B3 or X-B3-SpanID to affect the identification value recorded in the logs in foundations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34041.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-34041
- https://www.cloudfoundry.org/blog/abuse-of-http-hop-by-hop-headers-in-cloud-foundry-gorouter/
