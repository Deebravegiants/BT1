# [C] Lack of Input Validation in zendesk_api_client_php for Zendesk Subdomain

## Summary
Severity: Critical
Advisory: GHSA-q348-f93x-9gx4
CVE: CVE-2021-30492
CWE: CWE-20, CWE-918
Ecosystem: Packagist
Published: 2021-04-29
Source: https://github.com/advisories/GHSA-q348-f93x-9gx4
Type: github-advisory

## Affected
- Packagist: `zendesk/zendesk_api_client_php` — affected >=0 <2.2.11

## Details
### Impact
Lack of input validation of the Zendesk subdomain could expose users of the library to Server Side Request Forgery (SSRF).

### Resolution
Validate the provided Zendesk subdomain to be a valid subdomain in:
* getAuthUrl
* getAccessToken

## References
- https://github.com/zendesk/zendesk_api_client_php/security/advisories/GHSA-q348-f93x-9gx4
- https://github.com/zendesk/zendesk_api_client_php/pull/466
- https://github.com/zendesk/zendesk_api_client_php/commit/b451b743d9d6d81a9abf7cb86e70ec9c5332123e
