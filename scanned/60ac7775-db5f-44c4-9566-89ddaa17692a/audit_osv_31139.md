# [H] bpf: Reject struct_ops registration that uses module ptr and the module btf_id is missing

## Summary
Severity: High
Advisory: CVE-2024-58060
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58060
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Reject struct_ops registration that uses module ptr and the module btf_id is missing

There is a UAF report in the bpf_struct_ops when CONFIG_MODULES=n.
In particular, the report is on tcp_congestion_ops that has
a "struct module *owner" member.

For struct_ops that has a "struct module *owner" member,
it can be extended either by the regular kernel module or
by the bpf_struct_ops. bpf_try_module_get() will be used
to do the refcounting and different refcount is done
based on the owner pointer. When CONFIG_MODULES=n,
the btf_id of the "struct module" is missing:

WARN: resolve_btfids: unresolved symbol module

Thus, the bpf_try_module_get() cannot do the correct refcounting.

Not all subsystem's struct_ops requires the "struct module *owner" member.
e.g. the recent sched_ext_ops.

This patch is to disable bpf_struct_ops registration if
the struct_ops has the "struct module *" member and the
"struct module" btf_id is missing. The btf_type_is_fwd() helper
is moved to the btf.h header file for this test.

This has happened since the beginning of bpf_struct_ops which has gone
through many changes. The Fixes tag is set to a recent commit that this
patch can apply cleanly. Considering CONFIG_MODULES=n is not
common and the age of the issue, targeting for bpf-next also.

## References
- https://git.kernel.org/stable/c/2324fb4e92092837ee278fdd8d60c48ee1a619ce
- https://git.kernel.org/stable/c/96ea081ed52bf077cad6d00153b6fba68e510767
- https://git.kernel.org/stable/c/b777b14c2a4a4e2322daf8e8ffd42d2b88831b17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58060.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58060
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
