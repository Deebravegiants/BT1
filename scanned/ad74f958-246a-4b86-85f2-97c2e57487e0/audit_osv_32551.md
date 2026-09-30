# [M] EspoCRM allows unrestricted Embedding in Iframe dashlet

## Summary
Severity: Medium
Advisory: CVE-2025-32385
Aliases: GHSA-2rf2-mj98-2fr8
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32385
Type: osv

## Details
EspoCRM is an Open Source Customer Relationship Management software. Prior to 9.0.5, Iframe dashlet allows user to display iframes with arbitrary URLs. As the sandbox attribute is not included in the iframe, the remote page can open popups outside of the iframe, potentially tricking users and creating a phishing risk. The iframe URL is user-defined, so an attacker would need to trick the user into specifying a malicious URL. The missing sandbox attribute also allows the remote page to send messages to the parent frame. However, EspoCRM does not make use of these messages. This vulnerability is fixed in 9.0.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32385.json
- https://github.com/espocrm/espocrm/security/advisories/GHSA-2rf2-mj98-2fr8
- https://nvd.nist.gov/vuln/detail/CVE-2025-32385
