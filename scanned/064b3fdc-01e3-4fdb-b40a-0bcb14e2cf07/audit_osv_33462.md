# [M] Webapp DoS via malicious retrospective post in Playbooks

## Summary
Severity: Medium
Advisory: CVE-2025-41395
Aliases: GHSA-3g36-gf7c-75qw, GO-2025-3642
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-24
Source: https://osv.dev/vulnerability/CVE-2025-41395
Type: osv

## Details
Mattermost versions 10.4.x <= 10.4.2, 10.5.x <= 10.5.0, 9.11.x <= 9.11.10 fail to properly validate the props used by the RetrospectivePost custom post type in the Playbooks plugin, which allows an attacker to create a specially crafted post with maliciously crafted props and cause a denial of service (DoS) of the web app for all users.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/41xxx/CVE-2025-41395.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-41395
