# [C] Job Iteration API is vulnerable to OS Command Injection attack through its CsvEnumerator class

## Summary
Severity: Critical
Advisory: GHSA-6qjf-g333-pv38
CVE: CVE-2025-53623
CWE: CWE-78
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-14
Source: https://github.com/advisories/GHSA-6qjf-g333-pv38
Type: github-advisory

## Affected
- RubyGems: `job-iteration` — affected >=0 <1.11

## Details
### Impact
There is an arbitrary code execution vulnerability in the `CsvEnumerator` class of the `job-iteration` repository. This vulnerability can be exploited by an attacker to execute arbitrary commands on the system where the application is running, potentially leading to unauthorized access, data leakage, or complete system compromise.

### Patches
Issue is fixed in versions `1.11.0` and above.

### Workarounds
Users can mitigate the risk by avoiding the use of untrusted input in the `CsvEnumerator` class and ensuring that any file paths are properly sanitized and validated before being passed to the class methods. Users should avoid calling `count_of_rows_in_file` on enumerators constructed with untrusted CSV filenames.

## References
- https://github.com/Shopify/job-iteration/security/advisories/GHSA-6qjf-g333-pv38
- https://nvd.nist.gov/vuln/detail/CVE-2025-53623
- https://github.com/Shopify/job-iteration/pull/595
- https://github.com/Shopify/job-iteration/commit/1a7adfdd041105a5e45e774cadc6b973a292ba55
- https://github.com/Shopify/job-iteration
- https://github.com/Shopify/job-iteration/releases/tag/v1.11.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/job-iteration/CVE-2025-53623.yml
