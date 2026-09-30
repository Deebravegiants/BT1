# [H] CVE-2017-2295

## Summary
Severity: High
Advisory: CVE-2017-2295
CVSS: 8.2 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-2295
Type: osv

## Details
Versions of Puppet prior to 4.10.1 will deserialize data off the wire (from the agent to the server, in this case) with a attacker-specified format. This could be used to force YAML deserialization in an unsafe manner, which would lead to remote code execution. This change constrains the format of data on the wire to PSON or safely decoded YAML.

## References
- http://www.debian.org/security/2017/dsa-3862
- http://www.securityfocus.com/bid/98582
- https://puppet.com/security/cve/cve-2017-2295
