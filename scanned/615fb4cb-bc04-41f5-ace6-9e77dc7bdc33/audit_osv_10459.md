# [H] CVE-2017-15871

## Summary
Severity: High
Advisory: CVE-2017-15871
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-24
Source: https://osv.dev/vulnerability/CVE-2017-15871
Type: osv

## Details
The deserialize function in serialize-to-js through 1.1.1 allows attackers to cause a denial of service via vectors involving an Immediately Invoked Function Expression "function()" substring, as demonstrated by a "function(){console.log(" call or a simple infinite loop. NOTE: the vendor agrees that denial of service can occur but notes that deserialize is explicitly listed as "harmful" within the README.md file

## References
- https://github.com/commenthol/serialize-to-js/issues/3
- https://kay-malwarebenchmark.github.io/blog/cve-2017-15871-dos-through-iife/
