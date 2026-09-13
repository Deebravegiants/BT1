# [M] fgraph: Add READ_ONCE() when accessing fgraph_array[]

## Summary
Severity: Medium
Advisory: CVE-2024-57934
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2024-57934
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

fgraph: Add READ_ONCE() when accessing fgraph_array[]

In __ftrace_return_to_handler(), a loop iterates over the fgraph_array[]
elements, which are fgraph_ops. The loop checks if an element is a
fgraph_stub to prevent using a fgraph_stub afterward.

However, if the compiler reloads fgraph_array[] after this check, it might
race with an update to fgraph_array[] that introduces a fgraph_stub. This
could result in the stub being processed, but the stub contains a null
"func_hash" field, leading to a NULL pointer dereference.

To ensure that the gops compared against the fgraph_stub matches the gops
processed later, add a READ_ONCE(). A similar patch appears in commit
63a8dfb ("function_graph: Add READ_ONCE() when accessing fgraph_array[]").

## References
- https://git.kernel.org/stable/c/b68b2a3fbacc7be720ef589d489bcacdd05c6d38
- https://git.kernel.org/stable/c/d65474033740ded0a4fe9a097fce72328655b41d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57934.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57934
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
