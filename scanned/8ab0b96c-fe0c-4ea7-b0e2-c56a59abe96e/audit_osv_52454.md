# [M] CVE-2021-47465

## Summary
Severity: Medium
Advisory: CVE-2021-47465
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47465
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: PPC: Book3S HV: Fix stack handling in idle_kvm_start_guest()

In commit 10d91611f426 ("powerpc/64s: Reimplement book3s idle code in
C") kvm_start_guest() became idle_kvm_start_guest(). The old code
allocated a stack frame on the emergency stack, but didn't use the
frame to store anything, and also didn't store anything in its caller's
frame.

idle_kvm_start_guest() on the other hand is written more like a normal C
function, it creates a frame on entry, and also stores CR/LR into its
callers frame (per the ABI). The problem is that there is no caller
frame on the emergency stack.

The emergency stack for a given CPU is allocated with:

  paca_ptrs[i]->emergency_sp = alloc_stack(limit, i) + THREAD_SIZE;

So emergency_sp actually points to the first address above the emergency
stack allocation for a given CPU, we must not store above it without
first decrementing it to create a frame. This is different to the
regular kernel stack, paca->kstack, which is initialised to point at an
initial frame that is ready to use.

idle_kvm_start_guest() stores the backchain, CR and LR all of which
write outside the allocation for the emergency stack. It then creates a
stack frame and saves the non-volatile registers. Unfortunately the
frame it creates is not large enough to fit the non-volatiles, and so
the saving of the non-volatile registers also writes outside the
emergency stack allocation.

The end result is that we corrupt whatever is at 0-24 bytes, and 112-248
bytes above the emergency stack allocation.

In practice this has gone unnoticed because the memory immediately above
the emergency stack happens to be used for other stack allocations,
either another CPUs mc_emergency_sp or an IRQ stack. See the order of
calls to irqstack_early_init() and emergency_stack_init().

The low addresses of another stack are the top of that stack, and so are
only used if that stack is under extreme pressue, which essentially
never happens in practice - and if it did there's a high likelyhood we'd
crash due to that stack overflowing.

Still, we shouldn't be corrupting someone else's stack, and it is purely
luck that we aren't corrupting something else.

To fix it we save CR/LR into the caller's frame using the existing r1 on
entry, we then create a SWITCH_FRAME_SIZE frame (which has space for
pt_regs) on the emergency stack with the backchain pointing to the
existing stack, and then finally we switch to the new frame on the
emergency stack.

## References
- https://git.kernel.org/stable/c/6d077c37c4643394b1bae9682da48164fc147ea8
- https://git.kernel.org/stable/c/80bbb0bc3a0288442f7fe6fc514f4ee1cb06ccb7
- https://git.kernel.org/stable/c/9b4416c5095c20e110c82ae602c254099b83b72f
- https://git.kernel.org/stable/c/fbd724c49bead048ae9fc1a5b7bff2fb3e54f855
