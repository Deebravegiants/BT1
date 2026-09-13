# [H] CVE-2021-35196

## Summary
Severity: High
Advisory: CVE-2021-35196
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-21
Source: https://osv.dev/vulnerability/CVE-2021-35196
Type: osv

## Details
Manuskript through 0.12.0 allows remote attackers to execute arbitrary code via a crafted settings.pickle file in a project file, because there is insecure deserialization via the pickle.load() function in settings.py. NOTE: the vendor's position is that the product is not intended for opening an untrusted project file

## References
- https://github.com/olivierkes/manuskript/issues/891
- https://www.pizzapower.me/2021/06/20/arbitrary-code-execution-in-manuskript-0-12/
