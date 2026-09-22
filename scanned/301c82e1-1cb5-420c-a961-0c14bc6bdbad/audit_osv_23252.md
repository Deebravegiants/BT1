# [C] Code injection in pdfmake

## Summary
Severity: Critical
Advisory: CVE-2022-46161
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-12-06
Source: https://osv.dev/vulnerability/CVE-2022-46161
Type: osv

## Details
pdfmake is an open source client/server side PDF printing in pure JavaScript. In versions up to and including 0.2.5 pdfmake contains an unsafe evaluation of user controlled input. Users of pdfmake are thus subject to arbitrary code execution in the context of the process running the pdfmake code. There are no known fixes for this issue. Users are advised to restrict access to trusted user input.

## References
- https://github.com/bpampuch/pdfmake/blob/802813970ac6de68a0bd0931b74150b33da0dd18/dev-playground/server.js#L32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46161.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-46161
- https://securitylab.github.com/advisories/GHSL-2022-068_pdfmake/
