# [H] bpf: consider that tail calls invalidate packet pointers

## Summary
Severity: High
Advisory: CVE-2024-58237
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-05
Source: https://osv.dev/vulnerability/CVE-2024-58237
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.6.90, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: consider that tail calls invalidate packet pointers

Tail-called programs could execute any of the helpers that invalidate
packet pointers. Hence, conservatively assume that each tail call
invalidates packet pointers.

Making the change in bpf_helper_changes_pkt_data() automatically makes
use of check_cfg() logic that computes 'changes_pkt_data' effect for
global sub-programs, such that the following program could be
rejected:

    int tail_call(struct __sk_buff *sk)
    {
    	bpf_tail_call_static(sk, &jmp_table, 0);
    	return 0;
    }

    SEC("tc")
    int not_safe(struct __sk_buff *sk)
    {
    	int *p = (void *)(long)sk->data;
    	... make p valid ...
    	tail_call(sk);
    	*p = 42; /* this is unsafe */
    	...
    }

The tc_bpf2bpf.c:subprog_tc() needs change: mark it as a function that
can invalidate packet pointers. Otherwise, it can't be freplaced with
tailcall_freplace.c:entry_freplace() that does a tail call.

## References
- https://git.kernel.org/stable/c/1a4607ffba35bf2a630aab299e34dd3f6e658d70
- https://git.kernel.org/stable/c/1c2244437f9ad3dd91215f920401a14f2542dbfc
- https://git.kernel.org/stable/c/f1692ee23dcaaddc24ba407b269707ee5df1301f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58237.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58237
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
