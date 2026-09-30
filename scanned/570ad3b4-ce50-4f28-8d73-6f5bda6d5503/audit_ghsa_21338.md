# [C] Skipper vulnerable to SSRF via X-Skipper-Proxy

## Summary
Severity: Critical
Advisory: GHSA-f2rj-m42r-6jm2
CVE: CVE-2022-38580
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-25
Source: https://github.com/advisories/GHSA-f2rj-m42r-6jm2
Type: github-advisory

## Affected
- Go: `github.com/zalando/skipper` — affected >=0 <0.13.237

## Details
### Impact

Skipper prior to version v0.13.236 is vulnerable to server-side request forgery (SSRF). An attacker can exploit a vulnerable version of proxy to access the internal metadata server or other unauthenticated URLs by adding an specific header (X-Skipper-Proxy) to the http request.

### Patches
The problem was patched in version https://github.com/zalando/skipper/releases/tag/v0.13.237.
Users need to upgrade to skipper `>=v0.13.237`.

### Workarounds

Use `dropRequestHeader("X-Skipper-Proxy")` filter

### References

https://github.com/zalando/skipper/releases/tag/v0.13.237

### For more information
If you have any questions or comments about this advisory:

* Open an issue in https://github.com/zalando/skipper/issues/new/choose
* Chat with us in slack: https://app.slack.com/client/T029RQSE6/C82Q5JNH5

## References
- https://github.com/zalando/skipper/security/advisories/GHSA-f2rj-m42r-6jm2
- https://nvd.nist.gov/vuln/detail/CVE-2022-38580
- https://github.com/zalando/skipper/pull/2058
- https://github.com/zalando/skipper/commit/842634347da8fe77e396f66edea79d329fd72130
- https://gist.github.com/Fadavvi/9fffcfa4aaa9e25b77cfe7b3044b2857#file-cve-2022-38580
- https://github.com/zalando/skipper
- https://github.com/zalando/skipper/releases/tag/v0.13.237
- https://pastebin.com/dXxpgPAK
- https://pkg.go.dev/vuln/GO-2022-1086
- http://packetstormsecurity.com/files/171546/X-Skipper-Proxy-0.13.237-Server-Side-Request-Forgery.html
- http://skipper.com
- http://zalando.com
