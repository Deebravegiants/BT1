# [H] Label Studio allows Server-Side Request Forgery in the S3 Storage Endpoint

## Summary
Severity: High
Advisory: GHSA-m238-fmcw-wh58
CVE: CVE-2025-25297
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-02-14
Source: https://github.com/advisories/GHSA-m238-fmcw-wh58
Type: github-advisory

## Affected
- PyPI: `label-studio` — affected >=0 <1.16.0

## Details
## Description
Label Studio's S3 storage integration feature contains a Server-Side Request Forgery (SSRF) vulnerability in its endpoint configuration. When creating an S3 storage connection, the application allows users to specify a custom S3 endpoint URL via the s3_endpoint parameter. This endpoint URL is passed directly to the boto3 AWS SDK without proper validation or restrictions on the protocol or destination.

The vulnerability allows an attacker to make the application send HTTP requests to arbitrary internal services by specifying them as the S3 endpoint. When the storage sync operation is triggered, the application attempts to make S3 API calls to the specified endpoint, effectively making HTTP requests to the target service and returning the response in error messages.

This SSRF vulnerability enables attackers to bypass network segmentation and access internal services that should not be accessible from the external network. The vulnerability is particularly severe because error messages from failed requests contain the full response body, allowing data exfiltration from internal services.

## Steps to reproduce
1. Create an account in Label Studio

2. Create a new project with basic configuration

3. Create an S3 storage connection with the following configuration:
   ```json
   {
     "project": 1,
     "title": "Test Storage",
     "bucket": "<filename>",
     "s3_endpoint": "http://internal-web",
     "use_blob_urls": true,
     "aws_access_key_id": "test",
     "aws_secret_access_key": "test"
   }
   ```
4. Trigger a storage sync operation by sending a POST request to `/api/storages/s3/[storage_id]/sync`

The application will attempt to connect to the specified endpoint URL as if it were an S3 service. When the request fails due to invalid S3 API responses, the error message will contain the raw response from the internal service, allowing access to internal resources.
   
## Mitigations
- Implement strict validation of S3 endpoint URLs to allow only valid S3service endpoints
- Add an allowlist of endpoint domains and protocols
- Sanitize error messages to prevent leakage of sensitive information from failed requests
- Consider implementing network-level controls to restrict outbound connections from the application server

## Impact
This vulnerability has high severity as it allows authenticated users to make requests to arbitrary internal services from the application server, potentially exposing sensitive internal resources and bypassing network segmentation. The inclusion of response data in error messages makes this particularly effective for data exfiltration.

## References
- https://github.com/HumanSignal/label-studio/security/advisories/GHSA-m238-fmcw-wh58
- https://nvd.nist.gov/vuln/detail/CVE-2025-25297
- https://github.com/HumanSignal/label-studio/commit/06a2b29c1208e1878ccae66e6b84c8b24598fa79
- https://github.com/HumanSignal/label-studio
