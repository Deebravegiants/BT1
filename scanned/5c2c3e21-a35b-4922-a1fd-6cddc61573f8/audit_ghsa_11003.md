# [M] Rancher's weave CNI password is not configured when a cluster is created from an RKE template

## Summary
Severity: Medium
Advisory: GHSA-vrph-m5jj-c46c
CVE: CVE-2022-21951
CWE: CWE-311, CWE-319
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-vrph-m5jj-c46c
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.6.0 <2.6.5
- Go: `github.com/rancher/rancher` — affected >=2.5.0 <2.5.14

## Details
### Impact

This vulnerability only affects customers using [Weave](https://rancher.com/docs/rancher/v2.6/en/faq/networking/cni-providers/#weave) CNI (Container Network Interface) when configured through [RKE templates](https://rancher.com/docs/rancher/v2.6/en/admin-settings/rke-templates/).

A flaw was discovered in Rancher versions from 2.5.0 up to and including 2.5.13 and from 2.6.0 up to and including 2.6.4, where a UI (user interface) issue with RKE templates does not include a value for the Weave password when Weave is chosen as the CNI.

If a cluster is created based on the mentioned template and Weave is configured as the CNI, no password will be created for [network encryption](https://www.weave.works/docs/net/latest/tasks/manage/security-untrusted-networks/) in Weave, therefore network traffic in the cluster will be sent unencrypted.

This issue does not happen when a cluster, with Weave configured as CNI, is created without using an RKE template.

The impact of this vulnerability is higher when nodes on the cluster are on different locations and communicate with one another through the Internet, where monitoring (sniffing) of the network traffic by third-party entities can be more easily achieved.

### Patches

Patched versions include releases 2.5.14, 2.6.5 and later versions of Rancher. Besides upgrading to a Rancher patched version, the workarounds listed below must be applied in order for Weave to properly encrypt the network traffic.

### Workarounds

1. A manual password can be set in Weave by directly editing Weave's DaemonSet on the affected cluster to add the `WEAVE_PASSWORD` environment variable together with the a value for the password.

```shell
$ kubectl -n kube-system edit ds weave-net
```
```yaml
<snipped>
      containers:
      - command:
        - /home/weave/launch.sh
        env:
        - name: INIT_CONTAINER
          value: "true"
        - name: HOSTNAME
          valueFrom:
            fieldRef:
              apiVersion: v1
              fieldPath: spec.nodeName
        - name: IPALLOC_RANGE
          value: <IP allocation range>
        - name: WEAVE_PASSWORD
          value: "insert strong secret password here"
        image: <Weave image>
<snipped>
```
2. A new [RKE template revision](https://rancher.com/docs/rancher/v2.6/en/admin-settings/rke-templates/creating-and-revising/) must be created in order to properly generate the Weave password on new clusters.

**Notes**

1. In order to provide protection against brute-force attacks, that might break the network encryption, a strong password must be generated for the workaround. Weave's documentation provides recommendations for generating a [strong password](https://www.weave.works/docs/net/latest/tasks/manage/security-untrusted-networks/).

2. Manually generating the password for the workaround is only needed on affected versions of Rancher. This step is not needed when creating new RKE templates on patched versions of Rancher.

### For more information

If you have any questions or comments about this advisory:

* Reach out to [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
* Open an issue in [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
* Verify SUSE Rancher [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-vrph-m5jj-c46c
- https://nvd.nist.gov/vuln/detail/CVE-2022-21951
- https://bugzilla.suse.com/show_bug.cgi?id=1199443
- https://github.com/rancher/rancher
