# [M] CVE-2021-27099

## Summary
Severity: Medium
Advisory: CVE-2021-27099
Aliases: GHSA-q7gm-mjrg-44h9
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-03-05
Source: https://osv.dev/vulnerability/CVE-2021-27099
Type: osv

## Details
In SPIRE before versions 0.8.5, 0.9.4, 0.10.2, 0.11.3 and 0.12.1, the "aws_iid" Node Attestor improperly normalizes the path provided through the agent ID templating feature, which may allow the issuance of an arbitrary SPIFFE ID within the same trust domain, if the attacker controls the value of an EC2 tag prior to attestation, and the attestor is configured for agent ID templating where the tag value is the last element in the path. This issue has been fixed in SPIRE versions 0.11.3 and 0.12.1

## References
- https://github.com/spiffe/spire/security/advisories/GHSA-q7gm-mjrg-44h9
