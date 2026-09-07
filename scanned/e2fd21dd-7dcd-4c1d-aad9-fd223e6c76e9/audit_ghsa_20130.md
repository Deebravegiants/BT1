# [M] gotify/server vulnerable to Cross-site Scripting in the application image file upload

## Summary
Severity: Medium
Advisory: GHSA-xv6x-456v-24xh
CVE: CVE-2022-46181
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-30
Source: https://github.com/advisories/GHSA-xv6x-456v-24xh
Type: github-advisory

## Affected
- Go: `github.com/gotify/server` — affected >=0 <2.2.2

## Details
### Impact

The XSS vulnerability allows authenticated users to upload .html files. With that, an attacker could execute client side scripts **if** another user opened a link, such as:

```
https://push.example.org/image/[alphanumeric string].html
```

An attacker could potentially take over the account of the user that clicked the link. Keep in mind, the Gotify UI won't natively expose such a malicious link, so an attacker has to get the user to open the malicious link in a context outside of Gotify.

### Patches

The vulnerability has been fixed in version 2.2.2.

### Workarounds

You can block access to non image files via a reverse proxy in the `./image` directory.

### References

https://github.com/gotify/server/pull/534
https://github.com/gotify/server/pull/535

---

Thanks to rickshang (aka 无在无不在) for discovering and reporting this bug.

## References
- https://github.com/gotify/server/security/advisories/GHSA-xv6x-456v-24xh
- https://nvd.nist.gov/vuln/detail/CVE-2022-46181
- https://github.com/gotify/server/pull/534
- https://github.com/gotify/server/pull/535
- https://github.com/gotify/server
