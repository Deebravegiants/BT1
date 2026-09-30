# [M] bpf: Detect IP == ksym.end as part of BPF program

## Summary
Severity: Medium
Advisory: CVE-2023-52828
Ecosystem: Linux
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52828
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.202, >=5.11.0 <5.15.140, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Detect IP == ksym.end as part of BPF program

Now that bpf_throw kfunc is the first such call instruction that has
noreturn semantics within the verifier, this also kicks in dead code
elimination in unprecedented ways. For one, any instruction following
a bpf_throw call will never be marked as seen. Moreover, if a callchain
ends up throwing, any instructions after the call instruction to the
eventually throwing subprog in callers will also never be marked as
seen.

The tempting way to fix this would be to emit extra 'int3' instructions
which bump the jited_len of a program, and ensure that during runtime
when a program throws, we can discover its boundaries even if the call
instruction to bpf_throw (or to subprogs that always throw) is emitted
as the final instruction in the program.

An example of such a program would be this:

do_something():
	...
	r0 = 0
	exit

foo():
	r1 = 0
	call bpf_throw
	r0 = 0
	exit

bar(cond):
	if r1 != 0 goto pc+2
	call do_something
	exit
	call foo
	r0 = 0  // Never seen by verifier
	exit	//

main(ctx):
	r1 = ...
	call bar
	r0 = 0
	exit

Here, if we do end up throwing, the stacktrace would be the following:

bpf_throw
foo
bar
main

In bar, the final instruction emitted will be the call to foo, as such,
the return address will be the subsequent instruction (which the JIT
emits as int3 on x86). This will end up lying outside the jited_len of
the program, thus, when unwinding, we will fail to discover the return
address as belonging to any program and end up in a panic due to the
unreliable stack unwinding of BPF programs that we never expect.

To remedy this case, make bpf_prog_ksym_find treat IP == ksym.end as
part of the BPF program, so that is_bpf_text_address returns true when
such a case occurs, and we are able to unwind reliably when the final
instruction ends up being a call instruction.

## References
- https://git.kernel.org/stable/c/327b92e8cb527ae097961ffd1610c720481947f5
- https://git.kernel.org/stable/c/6058e4829696412457729a00734969acc6fd1d18
- https://git.kernel.org/stable/c/66d9111f3517f85ef2af0337ece02683ce0faf21
- https://git.kernel.org/stable/c/821a7e4143af115b840ec199eb179537e18af922
- https://git.kernel.org/stable/c/aa42a7cb92647786719fe9608685da345883878f
- https://git.kernel.org/stable/c/cf353904a82873e952633fcac4385c2fcd3a46e1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52828.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52828
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
