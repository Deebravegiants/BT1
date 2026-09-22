# [M] CVE-2022-23951

## Summary
Severity: Medium
Advisory: CVE-2022-23951
Aliases: GHSA-6xx7-m45w-76m2
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/CVE-2022-23951
Type: osv

## Details
In Keylime before 6.3.0, quote responses from the agent can contain possibly untrusted ZIP data which can lead to zip bombs.

## References
- https://seclists.org/oss-sec/2022/q1/101
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23951.json
- https://github.com/keylime/keylime/security/advisories/GHSA-6xx7-m45w-76m2
- https://nvd.nist.gov/vuln/detail/CVE-2022-23951
- https://github.com/keylime/keylime/commit/6e44758b64b0ee13564fc46e807f4ba98091c355
