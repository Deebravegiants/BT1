# [M] Improper Access Control in nltk/nltk

## Summary
Severity: Medium
Advisory: CVE-2026-12261
Aliases: PYSEC-2026-3954
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-12261
Type: osv

## Details
A vulnerability in `nltk.downloader` in nltk/nltk versions <= 3.9.4 allows for cross-package resource and model poisoning. The downloader extracts package archives into shared namespaces such as `corpora/` and `taggers/` instead of package-isolated roots, and validates package integrity only after the archive has been written and extracted. This design flaw enables one package to overwrite another package's trusted resources within the same namespace, making the changes immediately active through ordinary NLTK APIs. This issue persists across fresh interpreter restarts and can affect downstream workflows, including machine learning pipelines and reproducibility-sensitive environments.

## References
- https://huntr.com/bounties/8b8c381e-08a8-4e4f-bb46-a320c96a364f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12261.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-12261
