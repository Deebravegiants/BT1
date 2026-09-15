# [H] Untrusted JAR Code Execution in Multiple Stanford Interface Classes in nltk/nltk

## Summary
Severity: High
Advisory: CVE-2026-12252
Aliases: PYSEC-2026-2085
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2026-12252
Type: osv

## Details
In nltk/nltk versions 3.9.3 and earlier, five Stanford interface classes (StanfordPOSTagger, StanfordNERTagger, StanfordParser, StanfordDependencyParser, and StanfordNeuralDependencyParser) are vulnerable to untrusted JAR code execution. These classes accept user-controllable JAR paths and execute them via the `java()` function, which invokes `subprocess.Popen()` without integrity verification. This vulnerability is identical to CVE-2026-0848, which was fixed for StanfordSegmenter by adding SHA256 verification. However, the fix was not applied to these additional classes, leaving them susceptible to arbitrary code execution when loading untrusted JAR files.

## References
- https://huntr.com/bounties/f5c93982-0cc9-4e2e-bb85-1b6ab29a2efb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12252.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-12252
