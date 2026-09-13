# [C] CVE-2018-1264

## Summary
Severity: Critical
Advisory: CVE-2018-1264
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-05
Source: https://osv.dev/vulnerability/CVE-2018-1264
Type: osv

## Details
Cloud Foundry Log Cache, versions prior to 1.1.1, logs its UAA client secret on startup as part of its envstruct report. A remote attacker who has gained access to the Log Cache VM can read this secret, gaining all privileges held by the Log Cache UAA client. In the worst case, if this client is an admin, the attacker would gain complete control over the Foundation.

## References
- https://www.cloudfoundry.org/blog/cve-2018-1264/
