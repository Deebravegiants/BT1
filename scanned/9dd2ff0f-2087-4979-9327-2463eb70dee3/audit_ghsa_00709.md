# [H] The filename of uploaded files vulnerable to stored XSS

## Summary
Severity: High
Advisory: GHSA-68q3-7wjp-7q3j
CVE: CVE-2020-4041
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-06-09
Source: https://github.com/advisories/GHSA-68q3-7wjp-7q3j
Type: github-advisory

## Affected
- Packagist: `bolt/bolt` — affected >=0 <3.7.1

## Details
### Impact

The filename of uploaded files was vulnerable to stored XSS. It is not possible to inject javascript code in the file name when creating/uploading the file. But, once created/uploaded, it can be renamed to inject the payload in it. 

Additionally, the measures to prevent renaming the file to disallowed filename extensions could be circumvented.

### Patches

This is fixed in Bolt 3.7.1.

### References

Related issue: https://github.com/bolt/bolt/pull/7853

## References
- https://github.com/bolt/bolt/security/advisories/GHSA-68q3-7wjp-7q3j
- https://nvd.nist.gov/vuln/detail/CVE-2020-4041
- https://github.com/bolt/bolt/pull/7853
- https://github.com/bolt/bolt/commit/b42cbfcf3e3108c46a80581216ba03ef449e419f
- https://github.com/bolt/bolt
- http://packetstormsecurity.com/files/158299/Bolt-CMS-3.7.0-XSS-CSRF-Shell-Upload.html
- http://seclists.org/fulldisclosure/2020/Jul/4
