# [H] kiwitcms vulnerable to stored cross-site scripting via unrestricted file upload

## Summary
Severity: High
Advisory: GHSA-2fqm-m4r2-fh98
CVE: CVE-2023-33977
CWE: CWE-434, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-2fqm-m4r2-fh98
Type: github-advisory

## Affected
- PyPI: `kiwitcms` — affected >=0 <12.4

## Details
### Impact

Kiwi TCMS allows users to upload attachments to test plans, test cases, etc. Earlier versions of Kiwi TCMS had introduced upload validators in order to prevent potentially dangerous files from being uploaded and Content-Security-Policy definition to prevent cross-site-scripting attacks. 

The upload validation checks were not 100% robust which left the possibility to circumvent them and upload a potentially dangerous file which allows execution of arbitrary JavaScript in the browser. Additionally we've discovered that Nginx's `proxy_pass` directive will strip some headers negating protections built into Kiwi TCMS when served behind a reverse proxy.

### Patches

- Improved file upload validation code
- Updated Nginx reverse proxy configuration for ***.tenant.kiwitcms.org**

### Workarounds

If serving Kiwi TCMS behind a reverse proxy make sure that additional header values are still passed to the client browser. If they aren't redefine them inside the proxy configuration. See [etc/nginx.conf#L66-L68](https://github.com/kiwitcms/Kiwi/blob/master/etc/nginx.conf#L66-L68) and [etc/nginx.conf#L87](https://github.com/kiwitcms/Kiwi/blob/master/etc/nginx.conf#L87)

### References

Disclosed by [M Nadeem Qazi](https://huntr.dev/bounties/6aea9a26-e29a-467b-aa5a-f767f0c2ec96/).

## References
- https://github.com/kiwitcms/Kiwi/security/advisories/GHSA-2fqm-m4r2-fh98
- https://nvd.nist.gov/vuln/detail/CVE-2023-33977
- https://github.com/kiwitcms/kiwi/commit/d789f4b51025de4f8c747c037d02e1b0da80b034
- https://github.com/kiwitcms/Kiwi
- https://github.com/kiwitcms/Kiwi/blob/master/etc/nginx.conf#L66-L68
- https://github.com/kiwitcms/Kiwi/blob/master/etc/nginx.conf#L87
- https://huntr.dev/bounties/6aea9a26-e29a-467b-aa5a-f767f0c2ec96
- https://kiwitcms.org/blog/kiwi-tcms-team/2023/06/06/kiwi-tcms-124
