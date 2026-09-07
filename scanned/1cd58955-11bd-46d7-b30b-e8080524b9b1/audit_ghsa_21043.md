# [M] mangadex-downloader vulnerable to unauthorized file reading

## Summary
Severity: Medium
Advisory: GHSA-r9x7-2xmr-v8fw
CVE: CVE-2022-36082
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-r9x7-2xmr-v8fw
Type: github-advisory

## Affected
- PyPI: `mangadex-downloader` — affected >=1.3.0 <1.7.2

## Details
### Impact

When using `file:<location>` command and `<location>` is web URL location (http, https). mangadex-downloader will try to open and read a file in local disk if the content from online file is exist-as-a-file in victim computer

So far, the app only read the files and not execute it. But still, when someone reading your files without you knowing, it's very scary.

### Proof of Concept (PoC)

https://www.mansuf.link/unauthorized-file-read-in-mangadex-downloader-cve-2022-36082/

### Workarounds

Unfortunately, there is no workarounds to make it safe from this issue. But i suggest you double check the url before proceed to download or update to latest version ( >= 1.7.2)

### Patches

Fixed in version 1.7.2.
Commit patch: https://github.com/mansuf/mangadex-downloader/commit/439cc2825198ebc12b3310c95c39a8c7710c9b42

## References
- https://github.com/mansuf/mangadex-downloader/security/advisories/GHSA-r9x7-2xmr-v8fw
- https://nvd.nist.gov/vuln/detail/CVE-2022-36082
- https://github.com/mansuf/mangadex-downloader/commit/439cc2825198ebc12b3310c95c39a8c7710c9b42
- https://github.com/mansuf/mangadex-downloader
- https://github.com/pypa/advisory-database/tree/main/vulns/mangadex-downloader/PYSEC-2022-264.yaml
