# [H] CVE-2022-44036

## Summary
Severity: High
Advisory: CVE-2022-44036
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-03
Source: https://osv.dev/vulnerability/CVE-2022-44036
Type: osv

## Details
In b2evolution 7.2.5, if configured with admins_can_manipulate_sensitive_files, arbitrary file upload is allowed for admins, leading to command execution. NOTE: the vendor's position is that this is "very obviously a feature not an issue and if you don't like that feature it is very obvious how to disable it."

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/44xxx/CVE-2022-44036.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-44036
- https://github.com/b2evolution/b2evolution/issues/121
