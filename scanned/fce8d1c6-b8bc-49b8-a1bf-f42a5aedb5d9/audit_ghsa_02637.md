# [H] Uncontrolled Resource Consumption in ansi-html

## Summary
Severity: High
Advisory: GHSA-whgm-jr23-g3j9
CVE: CVE-2021-23424
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-whgm-jr23-g3j9
Type: github-advisory

## Affected
- npm: `ansi-html` — affected >=0 <0.0.8

## Details
This affects all versions of package ansi-html. If an attacker provides a malicious string, it will get stuck processing the input for an extremely long time.

## References
- https://github.com/ioet/time-tracker-ui/security/advisories/GHSA-4fjc-8q3h-8r69
- https://nvd.nist.gov/vuln/detail/CVE-2021-23424
- https://github.com/Tjatse/ansi-html/issues/19
- https://github.com/Tjatse/ansi-html/commit/8142b25bca3133ea060bcc1889277dc482327a63
- https://github.com/Tjatse/ansi-html
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1567198
- https://snyk.io/vuln/SNYK-JS-ANSIHTML-1296849
