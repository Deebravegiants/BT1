# [C] CVE-2021-36800

## Summary
Severity: Critical
Advisory: CVE-2021-36800
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-08-04
Source: https://osv.dev/vulnerability/CVE-2021-36800
Type: osv

## Details
Akaunting version 2.1.12 and earlier suffers from a code injection issue in the Money.php component of the application. A POST sent to /{company_id}/sales/invoices/{invoice_id} with an items[0][price] that includes a PHP callable function is executed directly. This issue was fixed in version 2.1.13 of the product.

## References
- https://www.rapid7.com/blog/post/2021/07/27/multiple-open-source-web-app-vulnerabilities-fixed/
