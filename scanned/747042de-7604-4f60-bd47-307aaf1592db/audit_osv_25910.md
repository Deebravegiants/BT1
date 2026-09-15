# [H] PILOS account takeover through password reset poisoning

## Summary
Severity: High
Advisory: CVE-2023-47107
Aliases: GHSA-mc6f-fj9h-5735
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-11-08
Source: https://osv.dev/vulnerability/CVE-2023-47107
Type: osv

## Details
PILOS is an open source front-end for BigBlueButton servers with a built-in load balancer. The password reset component deployed within PILOS uses the hostname supplied within the request host header when building a password reset URL. It may be possible to manipulate the URL sent to PILOS users when so that it points to the attackers server thereby disclosing the password reset token if/when the link is followed. This only affects local user accounts and requires the password reset option to be enabled. This issue has been patched in version 2.3.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/47xxx/CVE-2023-47107.json
- https://github.com/THM-Health/PILOS/security/advisories/GHSA-mc6f-fj9h-5735
- https://nvd.nist.gov/vuln/detail/CVE-2023-47107
