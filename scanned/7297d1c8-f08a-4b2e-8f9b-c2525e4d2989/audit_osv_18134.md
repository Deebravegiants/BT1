# [H] CVE-2020-24345

## Summary
Severity: High
Advisory: CVE-2020-24345
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-08-13
Source: https://osv.dev/vulnerability/CVE-2020-24345
Type: osv

## Details
JerryScript through 2.3.0 allows stack consumption via function a(){new new Proxy(a,{})}JSON.parse("[]",a). NOTE: the vendor states that the problem is the lack of the --stack-limit option

## References
- https://github.com/jerryscript-project/jerryscript/issues/3977
