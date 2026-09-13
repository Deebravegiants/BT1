# [H] Pygments vulnerable to Regular Expression Denial of Service (ReDoS)

## Summary
Severity: High
Advisory: GHSA-pq64-v7f5-gqh8
CVE: CVE-2021-27291
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-pq64-v7f5-gqh8
Type: github-advisory

## Affected
- PyPI: `Pygments` — affected >=1.1 <2.7.4

## Details
In pygments 1.1+, fixed in 2.7.4, the lexers used to parse programming languages rely heavily on regular expressions. Some of the regular expressions have exponential or cubic worst-case complexity and are vulnerable to ReDoS. By crafting malicious input, an attacker can cause a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27291
- https://github.com/pygments/pygments/commit/2e7e8c4a7b318f4032493773732754e418279a14
- https://gist.github.com/b-c-ds/b1a2cc0c68a35c57188575eb496de5ce
- https://github.com/pygments/pygments
- https://github.com/pypa/advisory-database/tree/main/vulns/pygments/PYSEC-2021-141.yaml
- https://lists.debian.org/debian-lts-announce/2021/03/msg00024.html
- https://lists.debian.org/debian-lts-announce/2021/05/msg00003.html
- https://lists.debian.org/debian-lts-announce/2021/05/msg00006.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GSJRFHALQ7E3UV4FFMFU2YQ6LUDHAI55
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WSLD67LFGXOX2K5YNESSWAS4AGZIJTUQ
- https://www.debian.org/security/2021/dsa-4878
- https://www.debian.org/security/2021/dsa-4889
