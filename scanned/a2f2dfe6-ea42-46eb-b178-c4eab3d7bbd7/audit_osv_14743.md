# [M] CVE-2019-11246

## Summary
Severity: Medium
Advisory: CVE-2019-11246
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-08-29
Source: https://osv.dev/vulnerability/CVE-2019-11246
Type: osv

## Details
The kubectl cp command allows copying files between containers and the user machine. To copy files from a container, Kubernetes runs tar inside the container to create a tar archive, copies it over the network, and kubectl unpacks it on the user’s machine. If the tar binary in the container is malicious, it could run any code and output unexpected, malicious results. An attacker could use this to write files to any path on the user’s machine when kubectl cp is called, limited only by the system permissions of the local user. Kubernetes affected versions include versions prior to 1.12.9, versions prior to 1.13.6, versions prior to 1.14.2, and versions 1.1, 1.2, 1.4, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11.

## References
- https://groups.google.com/forum/#%21topic/kubernetes-security-announce/NLs2TGbfPdo
- https://security.netapp.com/advisory/ntap-20190919-0003/
- https://github.com/kubernetes/kubernetes/pull/76788
