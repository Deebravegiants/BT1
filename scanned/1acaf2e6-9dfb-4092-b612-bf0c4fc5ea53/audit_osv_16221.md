# [H] CVE-2019-3780

## Summary
Severity: High
Advisory: CVE-2019-3780
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-08
Source: https://osv.dev/vulnerability/CVE-2019-3780
Type: osv

## Details
Cloud Foundry Container Runtime, versions prior to 0.28.0, deploys K8s worker nodes that contains a configuration file with IAAS credentials. A malicious user with access to the k8s nodes can obtain IAAS credentials allowing the user to escalate privileges to gain access to the IAAS account.

## References
- http://www.securityfocus.com/bid/107434
- https://www.cloudfoundry.org/blog/cve-2019-3780
