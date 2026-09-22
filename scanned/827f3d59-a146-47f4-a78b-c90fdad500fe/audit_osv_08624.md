# [H] CVE-2016-4977

## Summary
Severity: High
Advisory: CVE-2016-4977
Aliases: GHSA-7q9c-h23x-65fq
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-25
Source: https://osv.dev/vulnerability/CVE-2016-4977
Type: osv

## Details
When processing authorization requests using the whitelabel views in Spring Security OAuth 2.0.0 to 2.0.9 and 1.0.0 to 1.0.5, the response_type parameter value was executed as Spring SpEL which enabled a malicious user to trigger remote code execution via the crafting of the value for response_type.

## References
- http://www.openwall.com/lists/oss-security/2019/10/16/1
- https://lists.apache.org/thread.html/0841d849c23418c473ccb9183cbf41a317cb0476e44be48022ce3488%40%3Cdev.fineract.apache.org%3E
- https://lists.apache.org/thread.html/37d7e820fc65a768de3e096e98382d5529a52a039f093e59357d0bc0%40%3Cdev.fineract.apache.org%3E
- https://lists.apache.org/thread.html/5e6dd946635bbcc9e1f2591599ad0fab54f2dc3714196af3b17893f2%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/96c017115069408cec5e82ce1e6293facab398011f6db7e1befbe274%40%3Cdev.fineract.apache.org%3E
- https://pivotal.io/security/cve-2016-4977
