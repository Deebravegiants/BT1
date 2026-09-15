# [H] CVE-2020-35514

## Summary
Severity: High
Advisory: CVE-2020-35514
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2020-35514
Type: osv

## Details
An insecure modification flaw in the /etc/kubernetes/kubeconfig file was found in OpenShift. This flaw allows an attacker with access to a running container which mounts /etc/kubernetes or has local access to the node, to copy this kubeconfig file and attempt to add their own node to the OpenShift cluster. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability. This flaw affects versions before openshift4/ose-machine-config-operator v4.7.0-202105111858.p0.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1914714
