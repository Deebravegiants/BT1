# [H] Authlib has algorithm confusion with asymmetric public keys

## Summary
Severity: High
Advisory: GHSA-5357-c2jx-v7qh
CVE: CVE-2024-37568
CWE: CWE-284, CWE-327, CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-06-09
Source: https://github.com/advisories/GHSA-5357-c2jx-v7qh
Type: github-advisory

## Affected
- PyPI: `authlib` — affected >=0 <1.3.1

## Details
lepture Authlib before 1.3.1 has algorithm confusion with asymmetric public keys. Unless an algorithm is specified in a jwt.decode call, HMAC verification is allowed with any asymmetric public key. (This is similar to CVE-2022-29217 and CVE-2024-33663.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37568
- https://github.com/lepture/authlib/issues/654
- https://github.com/lepture/authlib
- https://github.com/pypa/advisory-database/tree/main/vulns/authlib/PYSEC-2024-52.yaml
- https://lists.debian.org/debian-lts-announce/2025/10/msg00032.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FHJI32SN4FNAUVNALVGOKWHNSQ6XS3M5
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IZI7HYGN7VZAYFV6UV3SRLYF7QGERXIU
- https://www.vicarius.io/vsociety/posts/algorithm-confusion-in-lepture-authlib-cve-2024-37568
