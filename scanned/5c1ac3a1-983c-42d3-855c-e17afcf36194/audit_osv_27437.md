# [M] CVE-2024-21527

## Summary
Severity: Medium
Advisory: CVE-2024-21527
Aliases: GO-2024-2996
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2024-07-19
Source: https://osv.dev/vulnerability/CVE-2024-21527
Type: osv

## Details
Versions of the package github.com/gotenberg/gotenberg/v8/pkg/gotenberg before 8.1.0; versions of the package github.com/gotenberg/gotenberg/v8/pkg/modules/chromium before 8.1.0; versions of the package github.com/gotenberg/gotenberg/v8/pkg/modules/webhook before 8.1.0 are vulnerable to Server-side Request Forgery (SSRF) via the /convert/html endpoint when a request is made to a file via localhost, such as <iframe src="\\localhost/etc/passwd">. By exploiting this vulnerability, an attacker can achieve local file inclusion, allowing of sensitive files read on the host system. WorkaroundAn alternative is using either or both --chromium-deny-list and --chromium-allow-list flags.

## References
- https://gist.github.com/filipochnik/bc88a3d1cc17c07cec391ee98e1e6356
- https://github.com/gotenberg/gotenberg/releases/tag/v8.1.0
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGOTENBERGGOTENBERGV8PKGGOTENBERG-7537081
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGOTENBERGGOTENBERGV8PKGMODULESCHROMIUM-7537082
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGOTENBERGGOTENBERGV8PKGMODULESWEBHOOK-7537083
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21527.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-21527
- https://github.com/gotenberg/gotenberg/commit/ad152e62e5124b673099a9103eb6e7f933771794
