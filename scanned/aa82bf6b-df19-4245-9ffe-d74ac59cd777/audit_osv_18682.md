# [H] CVE-2020-35381

## Summary
Severity: High
Advisory: CVE-2020-35381
Aliases: GHSA-8vrw-m3j9-j27c, GO-2021-0057
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-35381
Type: osv

## Details
jsonparser 1.0.0 allows attackers to cause a denial of service (panic: runtime error: slice bounds out of range) via a GET call.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/27EA7OGCELV7QFAGVIHODHWKMKGFVIUZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LJO5N7YTDEUSTKYTNA372CE6VHCZJWUG/
- https://github.com/buger/jsonparser/issues/219
