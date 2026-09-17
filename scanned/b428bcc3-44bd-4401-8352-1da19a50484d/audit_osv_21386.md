# [C] CVE-2021-42581

## Summary
Severity: Critical
Advisory: CVE-2021-42581
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-05-10
Source: https://osv.dev/vulnerability/CVE-2021-42581
Type: osv

## Details
Prototype poisoning in function mapObjIndexed in Ramda 0.27.0 and earlier allows attackers to compromise integrity or availability of application via supplying a crafted object (that contains an own property "__proto__") as an argument to the function. NOTE: the vendor disputes this because the observed behavior only means that a user can create objects that the user didn't know would contain custom prototypes

## References
- https://github.com/ramda/ramda/pull/3192
- https://jsfiddle.net/3pomzw5g/2/
