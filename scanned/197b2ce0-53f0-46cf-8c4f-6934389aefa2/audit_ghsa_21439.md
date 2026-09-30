# [C] Heap buffer overflow in GPU

## Summary
Severity: Critical
Advisory: GHSA-995f-9x5r-2rcj
CVE: CVE-2022-4135
CWE: CWE-787
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-25
Source: https://github.com/advisories/GHSA-995f-9x5r-2rcj
Type: github-advisory

## Affected
- npm: `electron` — affected >=19.0.0 <19.1.8

## Details
Heap buffer overflow in GPU in Google Chrome prior to 107.0.5304.121 allowed a remote attacker who had compromised the renderer process to potentially perform a sandbox escape via a crafted HTML page. (Chromium security severity: High)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4135
- https://github.com/electron/electron/pull/36444
- https://github.com/electron/electron/pull/36447
- https://chromereleases.googleblog.com/2022/11/stable-channel-update-for-desktop_24.html
- https://crbug.com/1392715
- https://security.gentoo.org/glsa/202305-10
