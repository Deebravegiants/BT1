# [M] BudiBase Server-Side Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-29010
Aliases: GHSA-9xg2-9mcv-985p
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-06
Source: https://osv.dev/vulnerability/CVE-2023-29010
Type: osv

## Details
Budibase is a low code platform for creating internal tools, workflows, and admin panels. Versions prior to 2.4.3 (07 March 2023) are vulnerable to Server-Side Request Forgery. This can lead to an attacker gaining access to a Budibase AWS secret key. Users of Budibase cloud need to take no action. Self-host users who run Budibase on the public internet and are using a cloud provider that allows HTTP access to metadata information should ensure that when they deploy Budibase live, their internal metadata endpoint is not exposed.

## References
- https://github.com/Budibase/budibase/commits/develop?after=93d6939466aec192043d8ac842e754f65fdf2e8a+594&branch=develop&qualified_name=refs%2Fheads%2Fdevelop
- https://github.com/Budibase/budibase/releases/tag/v2.4.3
- https://github.com/Budibase/budibase/security/advisories/GHSA-9xg2-9mcv-985p
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29010.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29010
