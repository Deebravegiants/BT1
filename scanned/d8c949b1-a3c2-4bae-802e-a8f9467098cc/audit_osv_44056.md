# [M] Unauthenticated Disclosure of Scraping Credentials and Bypass Configuration via RansomLook API

## Summary
Severity: Medium
Advisory: CVE-2026-78386
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78386
Type: osv

## Details
RansomLook exposed sensitive operator-side scraping configuration through multiple unauthenticated API responses. Location records associated with ransomware groups and markets were returned largely verbatim to unauthenticated callers whenever the location itself was not marked as private.


These records could contain internal fields such as header, which may include authentication headers, session cookies, or other credentials used to access monitored websites; init_script, which may contain logic used to bypass CAPTCHA, anti-bot protections, or paywalls; and browser, which discloses details about the scraping environment.


An unauthenticated remote attacker could query the affected API endpoints and obtain these values. Leaked authentication material could potentially be replayed against the monitored service, while disclosure of scraping and bypass logic could allow site operators or other attackers to identify and defeat RansomLook's collection mechanisms.


The patch introduces an explicit allowlist of fields permitted in public location records and strips all operator-side fields before returning data to unauthenticated users.


The accompanying change from <string:postname> to <path:postname> appears to be a functional correction allowing legitimate post titles containing / and does not, based on this patch alone, represent the security issue.

## References
- https://github.com/RansomLook/RansomLook/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78386.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78386
- https://github.com/RansomLook/RansomLook/commit/cc9182930306ff36c7b3424817d49f18df3c85d1
