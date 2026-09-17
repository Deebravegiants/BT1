# [M] CVE-2019-17554

## Summary
Severity: Medium
Advisory: CVE-2019-17554
Aliases: GHSA-mgh8-hcwj-h57v
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-12-04
Source: https://osv.dev/vulnerability/CVE-2019-17554
Type: osv

## Details
The XML content type entity deserializer in Apache Olingo versions 4.0.0 to 4.6.0 is not configured to deny the resolution of external entities. Request with content type "application/xml", which trigger the deserialization of entities, can be used to trigger XXE attacks.

## References
- https://lists.apache.org/thread.html/r6d03e45b81eab03580cf7f8bb51cb3e9a1b10a2cc0c6a2d3cc92ed0c%40%3Cannounce.apache.org%3E
- https://mail-archives.apache.org/mod_mbox/olingo-user/201912.mbox/%3CCAGSZ4d7Ty%3DL-n_iAzT6vcQp65BY29XZDS5tMoM8MdDrb1moM7A%40mail.gmail.com%3E
- http://packetstormsecurity.com/files/155619/Apache-Olingo-OData-4.6.x-XML-Injection.html
- https://seclists.org/bugtraq/2019/Dec/11
