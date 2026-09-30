# [M] Maliciously crafted evidence packet may cause denial of service

## Summary
Severity: Medium
Advisory: CVE-2022-31135
Aliases: GHSA-vj86-vfmg-q68v
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-07-07
Source: https://osv.dev/vulnerability/CVE-2022-31135
Type: osv

## Details
Akashi is an open source server implementation of the Attorney Online video game based on the Ace Attorney universe. Affected versions of Akashi are subject to a denial of service attack. An attacker can use a specially crafted evidence packet to make an illegal modification, causing a server crash. This can be used to mount a denial-of-service exploit. Users are advised to upgrade. There is no known workaround for this issue.

## References
- https://github.com/AttorneyOnline/akashi/security/advisories/GHSA-vj86-vfmg-q68v
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31135.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-31135
- https://github.com/AttorneyOnline/akashi/commit/5566cdfedddef1f219aee33477d9c9690bf2f78b
