# [C] Remote Code Execution in Halibut

## Summary
Severity: Critical
Advisory: GHSA-hpf7-4c2g-9chf
CVE: CVE-2021-31819
CWE: CWE-502
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-23
Source: https://github.com/advisories/GHSA-hpf7-4c2g-9chf
Type: github-advisory

## Affected
- NuGet: `Halibut` — affected >=0 <4.4.7

## Details
In Halibut versions prior to 4.4.7 there is a deserialisation vulnerability that could allow remote code execution on systems that already trust each other based on certificate verification.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31819
- https://advisories.octopus.com/adv/2021-08---Remote-Code-Execution-via-Deserialisation-in-the-Halibut-Protocol-(CVE-2021-31819).2250309681.html
- https://github.com/OctopusDeploy/Halibut
