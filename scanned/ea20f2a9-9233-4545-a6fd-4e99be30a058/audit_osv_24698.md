# [H] Apache Fineract: SSRF template type vulnerability in certain authenticated users

## Summary
Severity: High
Advisory: CVE-2023-25195
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-03-28
Source: https://osv.dev/vulnerability/CVE-2023-25195
Type: osv

## Details
Server-Side Request Forgery (SSRF) vulnerability in Apache Software Foundation Apache Fineract.
Authorized users with limited permissions can gain access to server and may be able to use server for any outbound traffic. 

This issue affects Apache Fineract: from 1.4 through 1.8.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25195.json
- https://lists.apache.org/thread/m58fdjmtkfp9h4c0r4l48rv995w3qhb6
- https://nvd.nist.gov/vuln/detail/CVE-2023-25195
