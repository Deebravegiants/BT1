# [M] Denial of Service in Gerbv

## Summary
Severity: Medium
Advisory: CVE-2023-4508
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-24
Source: https://osv.dev/vulnerability/CVE-2023-4508
Type: osv

## Details
A user able to control file input to Gerbv, between versions 2.4.0 and 2.10.0, can cause a crash and cause denial-of-service with a specially crafted Gerber RS-274X file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4508.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4508
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-4508
- https://github.com/gerbv/gerbv/issues/191
- https://github.com/gerbv/gerbv/commit/5517e22250e935dc7f86f64ad414aeae3dbcb36a
- https://github.com/gerbv/gerbv
