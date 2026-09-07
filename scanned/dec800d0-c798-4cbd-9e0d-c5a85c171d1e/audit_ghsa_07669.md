# [H] CediPay Affected by Improper Input Validation in Payment Processing

## Summary
Severity: High
Advisory: GHSA-wvr6-395c-5pxr
CVE: CVE-2026-26063
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-wvr6-395c-5pxr
Type: github-advisory

## Affected
- npm: `cedipay-core` — affected >=0 <1.2.3

## Details
A vulnerability in CediPay allows attackers to bypass input validation in the transaction API.

Affected users: All deployments running versions prior to the patched release.

Risk: Exploitation could result in unauthorized transactions, exposure of sensitive financial data, and compromise of payment integrity.

Severity: High — potential financial loss and reputational damage.

Patches
The issue has been fixed in version 1.2.3.

Users should upgrade to 1.2.3 or later immediately.

All versions earlier than 1.2.3 remain vulnerable.

Workarounds
If upgrading is not immediately possible:

Restrict API access to trusted networks or IP ranges.

Enforce strict input validation at the application layer.

Monitor transaction logs for anomalies or suspicious activity.

These mitigations reduce exposure but do not fully eliminate the vulnerability.

References
OWASP Input Validation Guidelines (owasp.org in Bing)

CWE-20: Improper Input Validation

GitHub Security Advisory Documentation (docs.github.com in Bing)

## References
- https://github.com/xpertforextradeinc/CediPay/security/advisories/GHSA-wvr6-395c-5pxr
- https://nvd.nist.gov/vuln/detail/CVE-2026-26063
- https://github.com/xpertforextradeinc/CediPay
