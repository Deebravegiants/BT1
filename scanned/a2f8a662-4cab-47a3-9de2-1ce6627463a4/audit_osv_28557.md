# [M] Improper Access Control Leads to Server-Side Request Forgery in Mautic

## Summary
Severity: Medium
Advisory: CVE-2024-3448
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2024-3448
Type: osv

## Details
Users with low privileges can perform certain AJAX actions.  In this vulnerability instance, improper access to ajax?action=plugin:focus:checkIframeAvailability leads to a Server-Side Request Forgery by analyzing the error messages returned from the back-end. Allowing an attacker to perform a port scan in the back-end. At the time of publication of the CVE no patch is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3448.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3448
- https://github.com/mautic/mautic
- https://huntr.com/bounties/4d72d300-92d6-4e3c-93d8-52fe47396ae0
