# [M] Aim Stored XSS through TEXT EXPLORER

## Summary
Severity: Medium
Advisory: GHSA-pmhg-f7wc-c97m
CVE: CVE-2024-8863
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-09-16
Source: https://github.com/advisories/GHSA-pmhg-f7wc-c97m
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=0

## Details
A vulnerability, which was classified as problematic, was found in aimhubio aim up to 3.24. Affected is the function dangerouslySetInnerHTML of the file textbox.tsx of the component Text Explorer. The manipulation of the argument query leads to cross site scripting. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8863
- https://github.com/aimhubio/aim
- https://rumbling-slice-eb0.notion.site/Stored-XSS-through-TEXT-EXPLORER-in-aimhubio-aim-d0f07b7194724950a673498546d80d43?pvs=4
- https://vuldb.com/?ctiid.277500
- https://vuldb.com/?id.277500
- https://vuldb.com/?submit.403203
