# [H] OpenCTI has Semi-Blind SSRF via Unvalidated External URL in Data Ingestion Feature

## Summary
Severity: High
Advisory: GHSA-ffm6-vvph-g5f5
CVE: CVE-2026-21887
CWE: CWE-20, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-ffm6-vvph-g5f5
Type: github-advisory

## Affected
- PyPI: `pycti` — affected >=0 <6.8.16

## Details
### Summary
The OpenCTI platform’s data ingestion feature accepts user-supplied URLs without validation and uses the Axios HTTP client with its default configuration (allowAbsoluteUrls: true). This allows attackers to craft requests to arbitrary endpoints, including internal services, because Axios will accept and process absolute URLs.

This results in a semi-blind SSRF, as responses may not be fully visible but can still impact internal systems.

### Impact
OpenCTI’s data ingestion feature can allow an attacker to make the application send HTTP requests to arbitrary internal or external endpoints. This means an attacker could reach internal services that are not exposed publicly, such as Elasticsearch, Redis, or RabbitMQ, and potentially extract sensitive data or manipulate internal components. In cloud environments, the attacker could target metadata services like AWS, Azure, or GCP to obtain credentials and configuration details, which could lead to full compromise of the infrastructure. Even though the SSRF is semi-blind and the attacker may not see the full response, the ability to interact with internal services can enable enumeration, data exfiltration, and in some cases remote code execution if internal APIs expose dangerous functionality.

## References
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-ffm6-vvph-g5f5
- https://nvd.nist.gov/vuln/detail/CVE-2026-21887
- https://github.com/OpenCTI-Platform/opencti
- https://github.com/pypa/advisory-database/tree/main/vulns/pycti/PYSEC-2026-118.yaml
