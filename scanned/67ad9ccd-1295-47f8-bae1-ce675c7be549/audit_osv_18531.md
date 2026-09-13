# [C] CVE-2020-28360

## Summary
Severity: Critical
Advisory: CVE-2020-28360
Aliases: GHSA-43ch-2h55-2vj7
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-23
Source: https://osv.dev/vulnerability/CVE-2020-28360
Type: osv

## Details
Insufficient RegEx in private-ip npm package v1.0.5 and below insufficiently filters reserved IP ranges resulting in indeterminate SSRF. An attacker can perform a large range of requests to ARIN reserved IP ranges, resulting in an indeterminable number of critical attack vectors, allowing remote attackers to request server-side resources or potentially execute arbitrary code through various SSRF techniques.

## References
- https://github.com/frenchbread/private-ip
- https://www.npmjs.com/package/private-ip
