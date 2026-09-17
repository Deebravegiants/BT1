# [M] CVE-2019-10175

## Summary
Severity: Medium
Advisory: CVE-2019-10175
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-06-28
Source: https://osv.dev/vulnerability/CVE-2019-10175
Type: osv

## Details
A flaw was found in the containerized-data-importer in virt-cdi-cloner, version 1.4, where the host-assisted cloning feature does not determine whether the requesting user has permission to access the Persistent Volume Claim (PVC) in the source namespace. This could allow users to clone any PVC in the cluster into their own namespace, effectively allowing access to other user's data.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10175
