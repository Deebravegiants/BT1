# [M] Weave Net clusters susceptible to MitM attacks via IPv6 rogue router advertisements

## Summary
Severity: Medium
Advisory: GHSA-59qg-grp7-5r73
CVE: CVE-2020-11091
CWE: CWE-350
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-27
Source: https://github.com/advisories/GHSA-59qg-grp7-5r73
Type: github-advisory

## Affected
- Go: `github.com/weaveworks/weave` — affected >=0 <2.6.3

## Details
### Impact
An attacker able to run a process as root in a container is able to respond to DNS requests from the host and thereby insert themselves as a fake service.

In a cluster with an IPv4 internal network, if IPv6 is not totally disabled on the host (via ipv6.disable=1 on the kernel cmdline), it will be either unconfigured or configured on some interfaces, but it’s pretty likely that ipv6 forwarding is disabled, ie /proc/sys/net/ipv6/conf//forwarding == 0. Also by default, /proc/sys/net/ipv6/conf//accept_ra == 1. The combination of these 2 sysctls means that the host accepts router advertisements and configure the IPv6 stack using them.

By sending “rogue” router advertisements, an attacker can reconfigure the host to redirect part or all of the IPv6 traffic of the host to the attacker controlled container.
Even if there was no IPv6 traffic before, if the DNS returns A (IPv4) and AAAA (IPv6) records, many HTTP libraries will try to connect via IPv6 first then fallback to IPv4, giving an opportunity to the attacker to respond.
If by chance you also have on the host a vulnerability like last year’s RCE in apt (CVE-2019-3462), you can now escalate to the host.

### Patches
Weave Net version 2.6.3 (to be released soon) will disable the accept_ra option on the veth devices that it creates.

### Workarounds
Users should not run containers with CAP_NET_RAW capability.  This has been the advice from Weave Net for years.
https://www.weave.works/docs/net/latest/kubernetes/kube-addon/#-securing-the-setup

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the Weave Net repo](https://github.com/weaveworks/weave/issues/new)
* Join the <a href="https://slack.weave.works/" target="_blank">Weave Users Slack</a>.

## References
- https://github.com/weaveworks/weave/security/advisories/GHSA-59qg-grp7-5r73
- https://nvd.nist.gov/vuln/detail/CVE-2020-11091
- https://github.com/weaveworks/weave/commit/15f21f1899060f7716c70a8555a084e836f39a60
