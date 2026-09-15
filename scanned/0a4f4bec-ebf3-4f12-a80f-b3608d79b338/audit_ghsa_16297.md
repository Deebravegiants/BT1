# [M] diffoscope Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-33w6-hvmq-gh4x
CVE: CVE-2024-25711
Ecosystem: PyPI
Published: 2024-02-27
Source: https://github.com/advisories/GHSA-33w6-hvmq-gh4x
Type: github-advisory

## Affected
- PyPI: `diffoscope` — affected >=0 <256

## Details
diffoscope before 256 allows directory traversal via an embedded filename in a GPG file. Contents of any file, such as ../.ssh/id_rsa, may be disclosed to an attacker. This occurs because the value of the gpg --use-embedded-filenames option is trusted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25711
- https://github.com/pypa/advisory-database/tree/main/vulns/diffoscope/PYSEC-2024-41.yaml
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OUNBANAWD6TZH2NRRV4YUIAXEHLUJQ47
- https://salsa.debian.org/reproducible-builds/diffoscope
- https://salsa.debian.org/reproducible-builds/diffoscope/-/commit/dfed769904c27d66a14a5903823d9c8c5aae860e
- https://salsa.debian.org/reproducible-builds/diffoscope/-/issues/361
