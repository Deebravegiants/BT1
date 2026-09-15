# [M] Internationalized Domain Names in Applications (IDNA) vulnerable to denial of service from specially crafted inputs to idna.encode

## Summary
Severity: Medium
Advisory: GHSA-jjg7-2v4v-x38h
CVE: CVE-2024-3651
CWE: CWE-1333, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-11
Source: https://github.com/advisories/GHSA-jjg7-2v4v-x38h
Type: github-advisory

## Affected
- PyPI: `idna` — affected >=0 <3.7

## Details
### Impact
A specially crafted argument to the `idna.encode()` function could consume significant resources. This may lead to a denial-of-service.

### Patches
The function has been refined to reject such strings without the associated resource consumption in version 3.7.

### Workarounds
Domain names cannot exceed 253 characters in length, if this length limit is enforced prior to passing the domain to the `idna.encode()` function it should no longer consume significant resources. This is triggered by arbitrarily large inputs that would not occur in normal usage, but may be passed to the library assuming there is no preliminary input validation by the higher-level application.

### References
* https://huntr.com/bounties/93d78d07-d791-4b39-a845-cbfabc44aadb

## References
- https://github.com/kjd/idna/security/advisories/GHSA-jjg7-2v4v-x38h
- https://nvd.nist.gov/vuln/detail/CVE-2024-3651
- https://github.com/kjd/idna/commit/1d365e17e10d72d0b7876316fc7b9ca0eebdd38d
- https://github.com/kjd/idna
- https://github.com/pypa/advisory-database/tree/main/vulns/idna/PYSEC-2024-60.yaml
- https://huntr.com/bounties/93d78d07-d791-4b39-a845-cbfabc44aadb
- https://lists.debian.org/debian-lts-announce/2024/05/msg00006.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4YQUPYH3SVZ5GFF2CDQ55FCM575AZTF2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/F2S5E23N6E52S46KGNYTDFB75LOC4N4D
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/S5IDLLD2IKSIVRBSLB34WTSYGLMWUFWF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ULSC7HBJKXB3BZV367WM5BR6DFEC4Z43
