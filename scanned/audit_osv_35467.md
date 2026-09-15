# [C] CVE-2025-9312

## Summary
Severity: Critical
Advisory: CVE-2025-9312
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-18
Source: https://osv.dev/vulnerability/CVE-2025-9312
Type: osv

## Details
A missing authentication enforcement vulnerability exists in the mutual TLS (mTLS) implementation used by System REST APIs and SOAP services in multiple WSO2 products. Due to improper validation of client certificate–based authentication in certain default configurations, the affected components may permit unauthenticated requests even when mTLS is enabled. This condition occurs when relying on the default mTLS settings for System REST APIs or when the mTLS authenticator is enabled for SOAP services, causing these interfaces to accept requests without enforcing additional authentication.

Successful exploitation allows a malicious actor with network access to the affected endpoints to gain administrative privileges and perform unauthorized operations. The vulnerability is exploitable only when the impacted mTLS flows are enabled and accessible in a given deployment. Other certificate-based authentication mechanisms such as Mutual TLS OAuth client authentication and X.509 login flows are not affected, and APIs served through the API Gateway of WSO2 API Manager remain unaffected.

## References
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2025-4494/
