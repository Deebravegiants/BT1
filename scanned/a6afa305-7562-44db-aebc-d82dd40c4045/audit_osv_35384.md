# [H] picklescan - Arbitrary Code Execution via lib2to3.pgen2.pgen.ParserGenerator.make_label Detection Bypass

## Summary
Severity: High
Advisory: CVE-2025-71343
Aliases: GHSA-p9w7-82w4-7q8m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2025-71343
Type: osv

## Details
picklescan before 0.0.30 fails to detect malicious pickle files that exploit lib2to3.pgen2.pgen.ParserGenerator.make_label function in the reduce method. Attackers can craft malicious pickle files with embedded code that evades detection but executes arbitrary commands when pickle.load() is called.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71343.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-p9w7-82w4-7q8m
- https://nvd.nist.gov/vuln/detail/CVE-2025-71343
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-lib2to3-pgen2-pgen-parsergenerator-make-label-detection-bypass
