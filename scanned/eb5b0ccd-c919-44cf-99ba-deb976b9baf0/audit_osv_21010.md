# [M] CVE-2021-3948

## Summary
Severity: Medium
Advisory: CVE-2021-3948
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2021-3948
Type: osv

## Details
An incorrect default permissions vulnerability was found in the mig-controller. Due to an incorrect cluster namespaces handling an attacker may be able to migrate a malicious workload to the target cluster, impacting confidentiality, integrity, and availability of the services located on that cluster.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2022017
