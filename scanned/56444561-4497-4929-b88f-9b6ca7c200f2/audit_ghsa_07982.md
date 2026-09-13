# [M] Indico Affected by Cross-Site-Scripting via material uploads

## Summary
Severity: Medium
Advisory: GHSA-jxc4-54g3-j7vp
CVE: CVE-2026-25739
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-jxc4-54g3-j7vp
Type: github-advisory

## Affected
- PyPI: `indico` — affected >=0 <3.3.10

## Details
### Impact
There is a Cross-Site-Scripting vulnerability when uploading certain file types as materials.

### Patches
You should to update to [Indico 3.3.10](https://github.com/indico/indico/releases/tag/v3.3.10) as soon as possible.
See [the docs](https://docs.getindico.io/en/stable/installation/upgrade/) for instructions on how to update.

Please be aware that to apply the fix itself updating is sufficient, but to benefit from the strict Content-Security-Policy we now apply by default for file downloads, you need to update your webserver config in case you use nginx with Indico's `STATIC_FILE_METHOD` set to `xaccelredirect` and add the following line to the `.xsf/indico/` location block (you can consult the Indico setup documentation for the full configuration snippet):

```nginx
add_header Content-Security-Policy $upstream_http_content_security_policy;
```

### Workarounds
- Use your webserver config to apply a strict CSP for material download endpoints.
- Only let trustworthy users create content (including material uploads, which speakers can typically do as well) on Indico.

### For more information
If you have any questions or comments about this advisory:

- Open a thread in [our forum](https://talk.getindico.io/)
- Email us privately at [indico-team@cern.ch](mailto:indico-team@cern.ch)

## References
- https://github.com/indico/indico/security/advisories/GHSA-jxc4-54g3-j7vp
- https://nvd.nist.gov/vuln/detail/CVE-2026-25739
- https://github.com/indico/indico
- https://github.com/indico/indico/releases/tag/v3.3.10
