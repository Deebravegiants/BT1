# [C] Arbitrary Code Execution in NLTK StanfordSegmenter via Untrusted JAR Loading

## Summary
Severity: Critical
Advisory: CVE-2026-0848
Aliases: PYSEC-2026-99
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-0848
Type: osv

## Details
NLTK versions <=3.9.2 are vulnerable to arbitrary code execution due to improper input validation in the StanfordSegmenter module. The module dynamically loads external Java .jar files without verification or sandboxing. An attacker can supply or replace the JAR file, enabling the execution of arbitrary Java bytecode at import time. This vulnerability can be exploited through methods such as model poisoning, MITM attacks, or dependency poisoning, leading to remote code execution. The issue arises from the direct execution of the JAR file via subprocess with unvalidated classpath input, allowing malicious classes to execute when loaded by the JVM.

## References
- https://huntr.com/bounties/08b109bb-ac24-403f-9422-1c246ce60202
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0848.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0848
