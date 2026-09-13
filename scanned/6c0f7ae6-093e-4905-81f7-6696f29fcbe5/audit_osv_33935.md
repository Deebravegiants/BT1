# [M] CVE-2025-52920

## Summary
Severity: Medium
Advisory: CVE-2025-52920
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-06-23
Source: https://osv.dev/vulnerability/CVE-2025-52920
Type: osv

## Details
Innoshop through 0.4.1 allows Insecure Direct Object Reference (IDOR) at multiple places within the frontend shop. Anyone can create a customer account and easily exploit these. Successful exploitation results in disclosure of the PII of other customers and the deletion of their reviews of products on the website. To be specific, an attacker could view the order details of any order by browsing to /en/account/orders/_ORDER_ID_ or use the address and billing information of other customers by manipulating the shipping_address_id and billing_address_id parameters when making an order (this information is then reflected in the receipt). Additionally, an attacker could delete the reviews of other users by sending a DELETE request to /en/account/reviews/_REVIEW_ID.

## References
- https://medium.com/@The_Hiker/how-i-found-multiple-cves-in-innoshop-0-4-1-12c8f84ad87f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52920.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52920
- https://github.com/innocommerce/innoshop
