# [H] CVE-2020-10792

## Summary
Severity: High
Advisory: CVE-2020-10792
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-20
Source: https://osv.dev/vulnerability/CVE-2020-10792
Type: osv

## Details
openITCOCKPIT through 3.7.2 allows remote attackers to configure the self::DEVELOPMENT or self::STAGING option by placing a hostname containing "dev" or "staging" in the HTTP Host header.

## References
- https://openitcockpit.io/2020/2020/03/23/openitcockpit-3-7-3-released/
- https://github.com/it-novum/openITCOCKPIT/commit/719410b9ffff7d7b29dba7aad58faceb5eff789f
