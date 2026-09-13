# [H] bpf: Preserve id of register in sync_linked_regs()

## Summary
Severity: High
Advisory: CVE-2026-45933
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45933
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Preserve id of register in sync_linked_regs()

sync_linked_regs() copies the id of known_reg to reg when propagating
bounds of known_reg to reg using the off of known_reg, but when
known_reg was linked to reg like:

known_reg = reg         ; both known_reg and reg get same id
known_reg += 4          ; known_reg gets off = 4, and its id gets BPF_ADD_CONST

now when a call to sync_linked_regs() happens, let's say with the following:

if known_reg >= 10 goto pc+2

known_reg's new bounds are propagated to reg but now reg gets
BPF_ADD_CONST from the copy.

This means if another link to reg is created like:

another_reg = reg       ; another_reg should get the id of reg but
                          assign_scalar_id_before_mov() sees
                          BPF_ADD_CONST on reg and assigns a new id to it.

As reg has a new id now, known_reg's link to reg is broken. If we find
new bounds for known_reg, they will not be propagated to reg.

This can be seen in the selftest added in the next commit:

0: (85) call bpf_get_prandom_u32#7    ; R0=scalar()
1: (57) r0 &= 255                     ; R0=scalar(smin=smin32=0,smax=umax=smax32=umax32=255,var_off=(0x0; 0xff))
2: (bf) r1 = r0                       ; R0=scalar(id=1,smin=smin32=0,smax=umax=smax32=umax32=255,var_off=(0x0; 0xff)) R1=scalar(id=1,smin=smin32=0,smax=umax=smax32=umax32=255,var_off=(0x0; 0xff))
3: (07) r1 += 4                       ; R1=scalar(id=1+4,smin=umin=smin32=umin32=4,smax=umax=smax32=umax32=259,var_off=(0x0; 0x1ff))
4: (a5) if r1 < 0xa goto pc+4         ; R1=scalar(id=1+4,smin=umin=smin32=umin32=10,smax=umax=smax32=umax32=259,var_off=(0x0; 0x1ff))
5: (bf) r2 = r0                       ; R0=scalar(id=2,smin=umin=smin32=umin32=6,smax=umax=smax32=umax32=255) R2=scalar(id=2,smin=umin=smin32=umin32=6,smax=umax=smax32=umax32=255)
6: (a5) if r1 < 0xe goto pc+2         ; R1=scalar(id=1+4,smin=umin=smin32=umin32=14,smax=umax=smax32=umax32=259,var_off=(0x0; 0x1ff))
7: (35) if r0 >= 0xa goto pc+1        ; R0=scalar(id=2,smin=umin=smin32=umin32=6,smax=umax=smax32=umax32=9,var_off=(0x0; 0xf))
8: (37) r0 /= 0
div by zero

When 4 is verified, r1's bounds are propagated to r0 but r0 also gets
BPF_ADD_CONST (bug).
When 5 is verified, r0 gets a new id (2) and its link with r1 is broken.

After 6 we know r1 has bounds [14, 259] and therefore r0 should have
bounds [10, 255], therefore the branch at 7 is always taken. But because
r0's id was changed to 2, r1's new bounds are not propagated to r0.
The verifier still thinks r0 has bounds [6, 255] before 7 and execution
can reach div by zero.

Fix this by preserving id in sync_linked_regs() like off and subreg_def.

## References
- https://git.kernel.org/stable/c/58059335e46537de682db84984f7716c813208c4
- https://git.kernel.org/stable/c/65d114b5270b62aefb820ecd6c3b7caeea8f895d
- https://git.kernel.org/stable/c/92a8cb1806adefb263cf096eab6705705cf7eee1
- https://git.kernel.org/stable/c/af9e89d8dd39530c8bd14c33ddf6b502df1071b6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45933.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45933
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
