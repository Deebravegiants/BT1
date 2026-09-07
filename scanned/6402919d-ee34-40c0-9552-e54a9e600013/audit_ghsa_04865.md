# [H] Flawfinder output manipulation via untrusted filenames and source text

## Summary
Severity: High
Advisory: GHSA-4c3c-r6p8-c863
CVE: CVE-2026-48813
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-4c3c-r6p8-c863
Type: github-advisory

## Affected
- PyPI: `flawfinder` — affected >=0 <2.0.20

## Details
### Impact

This vulnerability is an improper input neutralization issue leading to output manipulation, specifically, Terminal/ANSI Escape Sequence Injection and XML Injection:

* Terminal Output Spoofing: A malicious file whose name contains ANSI escape sequences can end up being included in flawfinder's standard terminal output, with many effects. For example, this might allow an attacker to hide critical scan results, falsely making it appear to a human reviewer that no security issues were found.

* CSV and XML Injection: Untrusted fields (such as filenames, categories, or code context text) were not properly sanitized when generating structured reports. An attacker could exploit this to corrupt CSV formats or inject arbitrary XML attributes into SonarQube outputs via output_sonar().

It impacts those who use flawfinder to evaluate intentionally malicious filenames or file contents.

The initial filename injection problem was reported by Dan Lenz https://www.linkedin.com/in/dan-lenz/

The other vulnerabilities were found by flawfinder project leader David A. Wheeler, GitHub david-a-wheeler, https://dwheeler.com/

### Patches

This issue has been fully patched in Version 2.0.20 (released 2026-05-16). All users should upgrade to version 2.0.20 or later immediately. If you use Python's package manager, you can upgrade using `pip install --upgrade flawfinder`. If you are consuming flawfinder via GitHub Actions, ensure your workflow points to david-a-wheeler/flawfinder@2.0.20 or later.

### Workarounds

There is no configuration-based workaround within older versions of flawfinder. If an immediate upgrade is not possible, users can mitigate the risk by:

* Pre-scanning filenames: Manually or programmatically verifying that target repositories do not contain filenames with control characters (including ANSI escape sequences) before passing them to flawfinder.

* Inspecting raw output: Reviewing flawfinder outputs in a text editor or logging mechanism that explicitly displays or strips raw escape sequences, rather than relying on live terminal rendering.

* Restricting untrusted inputs: Avoiding the generation of SonarQube or CSV reports from completely untrusted repositories until the tool is updated.

### Resources

See the flawfinder GitHub Repository: https://github.com/david-a-wheeler/flawfinder

## References
- https://github.com/david-a-wheeler/flawfinder/security/advisories/GHSA-4c3c-r6p8-c863
- https://nvd.nist.gov/vuln/detail/CVE-2026-48813
- https://github.com/david-a-wheeler/flawfinder
- https://github.com/pypa/advisory-database/tree/main/vulns/flawfinder/PYSEC-2026-2480.yaml
