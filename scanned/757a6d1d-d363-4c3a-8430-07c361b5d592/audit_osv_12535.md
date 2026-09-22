# [H] CVE-2018-1267

## Summary
Severity: High
Advisory: CVE-2018-1267
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-27
Source: https://osv.dev/vulnerability/CVE-2018-1267
Type: osv

## Details
Cloud Foundry Silk CNI plugin, versions prior to 0.2.0, contains an improper access control vulnerability. If the platform is configured with an application security group (ASG) that overlaps with the Silk overlay network, any applications can reach any other application on the network regardless of the configured routing policies.

## References
- https://www.cloudfoundry.org/blog/cve-2018-1267/
