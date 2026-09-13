# [M] Command Injection in pip when used with Mercurial

## Summary
Severity: Medium
Advisory: GHSA-mq26-g339-26xf
CVE: CVE-2023-5752
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-mq26-g339-26xf
Type: github-advisory

## Affected
- PyPI: `pip` — affected >=0 <23.3

## Details
When installing a package from a Mercurial VCS URL, e.g. `pip install hg+...`, with pip prior to v23.3, the specified Mercurial revision could be used to inject arbitrary configuration options to the `hg clone` call (e.g. `--config`). Controlling the Mercurial configuration can modify how and which repository is installed. This vulnerability does not affect users who aren't installing from Mercurial.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5752
- https://github.com/pypa/pip/pull/12306
- https://github.com/pypa/pip/commit/389cb799d0da9a840749fcd14878928467ed49b4
- https://github.com/pypa/advisory-database/tree/main/vulns/pip/PYSEC-2023-228.yaml
- https://github.com/pypa/pip
- https://lists.debian.org/debian-lts-announce/2025/10/msg00028.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/622OZXWG72ISQPLM5Y57YCVIMWHD4C3U
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/65UKKF5LBHEFDCUSPBHUN4IHYX7SRMHH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FXUVMJM25PUAZRQZBF54OFVKTY3MINPW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KFC2SPFG5FLCZBYY2K3T5MFW2D22NG6E
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YBSB3SUPQ3VIFYUMHPO3MEQI4BJAXKCZ
- https://mail.python.org/archives/list/security-announce@python.org/thread/F4PL35U6X4VVHZ5ILJU3PWUWN7H7LZXL
