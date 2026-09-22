# [H] netfilter: cttimeout: detach dataplane timeout policy and repurpose refcount

## Summary
Severity: High
Advisory: CVE-2026-74347
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74347
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: cttimeout: detach dataplane timeout policy and repurpose refcount

Add a refcount for struct nf_ct_timeout which is used by ct extension to
set the custom ct timeout policy, this tells us that the ct timeout is
being used by a conntrack entry. When the last conntrack entry drops the
refcount on the ct timeout, the ct timeout is released.

Remove the refcount for control plane which controls if the ruleset
refers to the timeout policy. After this update, it is possible to
remove the ct timeout policy from nfnetlink_cttimeout immediately.
This is for simplicity not to handle two refcounts on a single object.

Remove nf_queue_nf_hook_drop(): a packet sitting in nfqueue will just
hold a reference to the nf_ct_timeout object until packet is reinjected,
since this is part of the ct extension, this will be released by the
time the conntrack is freed.

nf_ct_untimeout() is still called to clean up in a best effort basis:
the ct timeout on existing entries gets removed when the ct timeout goes
away, but as long as the iptables ruleset still refers to the ct timeout
through a template, new conntracks may keep attaching it and extend its
lifetime until the rule is removed.

nf_ct_untimeout() is not called anymore from module removal path, this
is unlikely to find timeouts give module refcount is bumped, and the new
refcount already tracks the ct timeout policy use so it is released when
unused.

## References
- https://git.kernel.org/stable/c/7d6a9cdb8d3a51d9cfe546a09a518ab3d2671549
- https://git.kernel.org/stable/c/9aeb0dcfeb460d33d61d434148b51103ab1d2013
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74347.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74347
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
