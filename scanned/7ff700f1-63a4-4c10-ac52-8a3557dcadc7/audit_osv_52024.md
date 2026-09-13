# [H] CVE-2021-46978

## Summary
Severity: High
Advisory: CVE-2021-46978
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-46978
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: nVMX: Always make an attempt to map eVMCS after migration

When enlightened VMCS is in use and nested state is migrated with
vmx_get_nested_state()/vmx_set_nested_state() KVM can't map evmcs
page right away: evmcs gpa is not 'struct kvm_vmx_nested_state_hdr'
and we can't read it from VP assist page because userspace may decide
to restore HV_X64_MSR_VP_ASSIST_PAGE after restoring nested state
(and QEMU, for example, does exactly that). To make sure eVMCS is
mapped /vmx_set_nested_state() raises KVM_REQ_GET_NESTED_STATE_PAGES
request.

Commit f2c7ef3ba955 ("KVM: nSVM: cancel KVM_REQ_GET_NESTED_STATE_PAGES
on nested vmexit") added KVM_REQ_GET_NESTED_STATE_PAGES clearing to
nested_vmx_vmexit() to make sure MSR permission bitmap is not switched
when an immediate exit from L2 to L1 happens right after migration (caused
by a pending event, for example). Unfortunately, in the exact same
situation we still need to have eVMCS mapped so
nested_sync_vmcs12_to_shadow() reflects changes in VMCS12 to eVMCS.

As a band-aid, restore nested_get_evmcs_page() when clearing
KVM_REQ_GET_NESTED_STATE_PAGES in nested_vmx_vmexit(). The 'fix' is far
from being ideal as we can't easily propagate possible failures and even if
we could, this is most likely already too late to do so. The whole
'KVM_REQ_GET_NESTED_STATE_PAGES' idea for mapping eVMCS after migration
seems to be fragile as we diverge too much from the 'native' path when
vmptr loading happens on vmx_set_nested_state().

## References
- https://git.kernel.org/stable/c/200a45649ab7361bc80c70aebf7165b64f9a6c9f
- https://git.kernel.org/stable/c/bd0e8455b85b651a4c77de9616e307129b15aaa7
- https://git.kernel.org/stable/c/c8bf64e3fb77cc19bad146fbe26651985b117194
- https://git.kernel.org/stable/c/f5c7e8425f18fdb9bdb7d13340651d7876890329
