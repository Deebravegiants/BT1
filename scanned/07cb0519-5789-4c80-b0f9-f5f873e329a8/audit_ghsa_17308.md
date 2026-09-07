# [H] Grav is vulnerable to Server-Side Template Injection (SSTI) via Forms

## Summary
Severity: High
Advisory: GHSA-8535-hvm8-2hmv
CVE: CVE-2025-66298
CWE: CWE-1336
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-8535-hvm8-2hmv
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.8.0-beta.27

## Details
### Summary
Having a simple form on site can reveal the whole Grav configuration details (including plugin configuration details) by using the correct POST payload. Sensitive information may be contained in the configuration details.

### PoC
Create a simple form with two fields, 'registration-number' and 'hp'. Add a submit button and set the method to POST(screenshot attached below). Form name set to 'hero-form'. Send a POST request with the following payload and you will notice a response with a php array listing the whole Grav configuration details - including plugins(screenshot attached).

registration-number:d643aaaa

hp:vJyifp

__form-name__:hero-form

__unique_form_id__:{{var_dump(_context|slice(0,7))}}


![Screenshot 2025-03-25 at 7 26 02 AM](https://github.com/user-attachments/assets/b92b099b-c07a-4ea2-a3f9-47361ceb9355)

![Screenshot 2025-03-25 at 7 22 58 AM](https://github.com/user-attachments/assets/d9146fd3-5887-4bf8-87d9-78f43ade91c8)


### Impact
Server-Side Template (SST) vulnerability. The vulnerability affects the latest Grav version as of 25th of Match 2025 (1.7.48) with all plugins installed (including forms plugin v.7.4.2) to their latest versions as well.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-8535-hvm8-2hmv
- https://nvd.nist.gov/vuln/detail/CVE-2025-66298
- https://github.com/getgrav/grav/commit/e37259527d9c1deb6200f8967197a9fa587c6458
- https://github.com/getgrav/grav
