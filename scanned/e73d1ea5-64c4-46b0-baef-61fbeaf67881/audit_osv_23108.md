# [H] CVE-2022-43285

## Summary
Severity: High
Advisory: CVE-2022-43285
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-28
Source: https://osv.dev/vulnerability/CVE-2022-43285
Type: osv

## Details
Nginx NJS v0.7.4 was discovered to contain a segmentation violation in njs_promise_reaction_job. NOTE: the vendor disputes the significance of this report because NJS does not operate on untrusted input.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43285.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43285
- https://github.com/nginx/njs/issues/533
