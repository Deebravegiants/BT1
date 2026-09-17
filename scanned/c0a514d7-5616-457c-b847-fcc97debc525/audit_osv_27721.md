# [C] CVE-2024-25180

## Summary
Severity: Critical
Advisory: CVE-2024-25180
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2024-25180
Type: osv

## Details
An issue discovered in pdfmake 0.2.9 allows remote attackers to run arbitrary code via crafted POST request to the /pdf endpoint. NOTE: this is disputed because the behavior of the /pdf endpoint is intentional. The /pdf endpoint is only available after installing a test framework (that lives outside of the pdfmake applicaton). Anyone installing this is responsible for ensuring that it is only available to authorized testers.

## References
- https://github.com/joaoviictorti/My-CVES/blob/main/CVE-2024-25180/README.md
- https://security.snyk.io/vuln/SNYK-JS-PDFMAKE-6347243
- https://www.youtube.com/watch?v=QcOlrWUGo6o
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25180.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25180
- https://github.com/bpampuch/pdfmake/issues/2702
