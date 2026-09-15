# [M] Remote for TLS session may be trusted despite constraints in Pluto lang

## Summary
Severity: Medium
Advisory: CVE-2024-32973
Aliases: GHSA-84hj-7j2v-w665
CVSS: 4.8 (CVSS:3.1/AV:A/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-32973
Type: osv

## Details
Pluto is a superset of Lua 5.4 with a focus on general-purpose programming. In affected versions an attacker with the ability to actively intercept network traffic would be able to use a specifically-crafted certificate to fool Pluto into trusting it to be the intended remote for the TLS session. This results in the HTTP library and socket.starttls providing less transport integrity than expected. This issue has been patched in pull request #851 which has been included in version 0.9.3. Users are advised to upgrade. there are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32973.json
- https://github.com/PlutoLang/Pluto/security/advisories/GHSA-84hj-7j2v-w665
- https://nvd.nist.gov/vuln/detail/CVE-2024-32973
- https://github.com/PlutoLang/Pluto/pull/851
