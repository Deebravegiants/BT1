# [H] CVE-2025-63387

## Summary
Severity: High
Advisory: CVE-2025-63387
Aliases: PYSEC-2025-103
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-63387
Type: osv

## Details
Dify v1.9.1 is vulnerable to Insecure Permissions. An unauthenticated attacker can directly send HTTP GET requests to the /console/api/system-features endpoint without any authentication credentials or session tokens. The endpoint fails to implement proper authorization checks, allowing anonymous access to sensitive system configuration data. NOTE: The maintainer states that the endpoint is unauthenticated by design and serves as a bootstrap mechanism required for the dashboard initialization. They also state that the description inaccurately classifies the returned data as sensitive system configuration, stating that the data is non-sensitive and required for client-side rendering. No PII, credentials, or secrets are exposed.

## References
- https://gist.github.com/Cristliu/cddc0cbbf354de51106ab63a11be94af
- https://gist.github.com/Cristliu/dfc5f3a31dc6d7fff2754867e5c649a5
- https://github.com/langgenius/dify/discussions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63387.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63387
- https://github.com/langgenius/dify/issues/31368#issuecomment-3783712203
- https://github.com/langgenius/dify/pull/31392
- https://github.com/langgenius/dify/pull/31417
