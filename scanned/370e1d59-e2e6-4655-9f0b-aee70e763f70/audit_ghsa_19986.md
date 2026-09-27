# [M] Prometheus Exporter-Toolkit is vulnerable to authentication bypass

## Summary
Severity: Medium
Advisory: GHSA-7rg2-cxvp-9p7p
CVE: CVE-2022-46146
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-02
Source: https://github.com/advisories/GHSA-7rg2-cxvp-9p7p
Type: github-advisory

## Affected
- Go: `github.com/prometheus/exporter-toolkit` — affected >=0 <0.7.2
- Go: `github.com/prometheus/exporter-toolkit` — affected >=0.8.0 <0.8.2

## Details
### Impact

Prometheus and its exporters can be secured by a web.yml file that specifies usernames and hashed passwords for basic authentication.

Passwords are hashed with bcrypt, which means that even if you have access to the hash, it is very hard to find the original password back.

However, a flaw in the way this mechanism was implemented in the exporter toolkit makes it possible with people who know the hashed password to authenticate against Prometheus.

A request can be forged by an attacker to poison the internal cache used to cache the computation of hashes and make subsequent requests successful. This cache is used in both happy and unhappy scenarios in order to limit side channel attacks that could tell an attacker if a user is present in the file or not.

### Patches

The exporter-toolkit v0.7.3 and v0.8.2 have been released to address this issue.

### Workarounds

There is no workaround but attacker must have access to the hashed password, stored in disk, to bypass the authentication.

### Credit

We want to thank Lei Wan reporting this security issue.

## References
- https://github.com/prometheus/exporter-toolkit/security/advisories/GHSA-7rg2-cxvp-9p7p
- https://nvd.nist.gov/vuln/detail/CVE-2022-46146
- https://github.com/prometheus/exporter-toolkit/commit/25288779bc59d00c41b4a1706c6b87f0561ef2d7
- https://github.com/prometheus/exporter-toolkit/commit/5b1eab34484ddd353986bce736cd119d863e4ff5
- https://github.com/prometheus/exporter-toolkit
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JRSHISR64L6QGSMDFZDNPHHIXSCAKK26
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UH24VXIB25OGHF4VGY4PLZMTGTI3BHCA
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ULVDTAI76VATRAHTKCE2SUJ4NC3PQZ6Y
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JRSHISR64L6QGSMDFZDNPHHIXSCAKK26
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UH24VXIB25OGHF4VGY4PLZMTGTI3BHCA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ULVDTAI76VATRAHTKCE2SUJ4NC3PQZ6Y
- https://security.gentoo.org/glsa/202401-15
- http://www.openwall.com/lists/oss-security/2022/11/29/1
- http://www.openwall.com/lists/oss-security/2022/11/29/2
- http://www.openwall.com/lists/oss-security/2022/11/29/4
