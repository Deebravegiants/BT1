# [H] ReDoS Vulnerability in gaizhenbiao/chuanhuchatgpt

## Summary
Severity: High
Advisory: CVE-2024-6038
Aliases: PYSEC-2024-318
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-27
Source: https://osv.dev/vulnerability/CVE-2024-6038
Type: osv

## Details
A Regular Expression Denial of Service (ReDoS) vulnerability exists in the latest version of gaizhenbiao/chuanhuchatgpt. The vulnerability is located in the filter_history function within the utils.py module. This function takes a user-provided keyword and attempts to match it against chat history filenames using a regular expression search. Due to the lack of sanitization or validation of the keyword parameter, an attacker can inject a specially crafted regular expression, leading to a denial of service condition. This can cause severe degradation of service performance and potential system unavailability.

## References
- https://huntr.com/bounties/d41cca0a-82bc-4cbf-a52a-928d304fb42d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6038.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6038
- https://github.com/gaizhenbiao/chuanhuchatgpt/commit/fcdd5fd6b05ef537a1db185ab115758d87e1ba3f
