# [C] LNbits Lightning Network Payment System Vulnerable to Server-Side Request Forgery via LNURL Authentication Callback

## Summary
Severity: Critical
Advisory: GHSA-qp8j-p87f-c8cc
CVE: CVE-2025-32013
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-qp8j-p87f-c8cc
Type: github-advisory

## Affected
- PyPI: `lnbits` — affected >=0

## Details
# Server-Side Request Forgery via LNURL Authentication Callback in LNbits Lightning Network Payment System

## Disclaimer

This vulnerability was detected using **[XBOW](https://xbow.com/)**, a system that autonomously finds and exploits potential security vulnerabilities. The finding has been thoroughly reviewed and validated by a security researcher before submission. While XBOW is intended to work autonomously, during its development human experts ensure the accuracy and relevance of its reports.

## Description

A Server-Side Request Forgery (SSRF) vulnerability has been discovered in LNbits' LNURL authentication handling functionality. The vulnerability exists in the LNURL authentication callback process where the application makes HTTP requests to user-provided callback URLs and follows redirects without proper validation.

When processing LNURL authentication requests, the application accepts a callback URL parameter and makes an HTTP request to that URL using the httpx library with redirect following enabled. The application doesn't properly validate the callback URL, allowing attackers to specify internal network addresses and access internal resources.

This vulnerability allows an attacker to make the application send HTTP requests to arbitrary internal network locations, potentially exposing sensitive information or accessing internal services that should not be accessible from the internet.

## Steps to Reproduce

1. Create a new wallet account to get an admin key:

```
curl -X POST http://target:5000/api/v1/account -d '{"name":"test"}'
```

2. Use the obtained admin key to send a crafted LNURL authentication request:

```
curl -X POST http://target:5000/api/v1/lnurlauth \
  -H "X-Api-Key: <admin_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "callback": "http://target-internal-server/?tag=login&k1=9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
    "k1": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
    "sig": "0"*128,
    "key": "0"*64
  }'
```

The application will make an HTTP request to the internal URL specified in the callback parameter and return its contents in the response, allowing access to internal resources that should not be accessible.

## Mitigations

- Implement strict URL validation for callback URLs, ensuring they only point to allowed domains and networks.
- Use a whitelist of allowed domains and IP ranges for callback URLs.
- Disable redirect following in HTTP requests or implement strict redirect validation.
- Consider using a proxy service that restricts access to internal networks when making external HTTP requests.

## Impact

This vulnerability allows authenticated attackers to access internal network resources that should not be accessible from the internet. While authentication is required to exploit this vulnerability, any user who can create a wallet gets the necessary access level. The vulnerability can be used to read internal files, access internal services, and potentially expose sensitive information from the internal network.

## Disclosure Policy

This bug is subject to a 90-day disclosure deadline. If a fix for this issue is made available to users before the end of the 90-day deadline, this bug report will become public 15 days after the fix was made available. Regardless of this disclosure process, XBOW may privately notify other affected parties as soon as we become aware of this vulnerability.

## References
- https://github.com/lnbits/lnbits/security/advisories/GHSA-qp8j-p87f-c8cc
- https://nvd.nist.gov/vuln/detail/CVE-2025-32013
- https://github.com/lnbits/lnbits
- https://github.com/pypa/advisory-database/tree/main/vulns/lnbits/PYSEC-2025-16.yaml
