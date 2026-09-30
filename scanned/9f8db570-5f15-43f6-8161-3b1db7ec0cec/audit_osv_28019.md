# [H] KVM: x86/pmu: Disable support for adaptive PEBS

## Summary
Severity: High
Advisory: CVE-2024-26992
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26992
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.88, >=6.2.0 <6.6.29, >=6.7.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86/pmu: Disable support for adaptive PEBS

Drop support for virtualizing adaptive PEBS, as KVM's implementation is
architecturally broken without an obvious/easy path forward, and because
exposing adaptive PEBS can leak host LBRs to the guest, i.e. can leak
host kernel addresses to the guest.

Bug #1 is that KVM doesn't account for the upper 32 bits of
IA32_FIXED_CTR_CTRL when (re)programming fixed counters, e.g
fixed_ctrl_field() drops the upper bits, reprogram_fixed_counters()
stores local variables as u8s and truncates the upper bits too, etc.

Bug #2 is that, because KVM _always_ sets precise_ip to a non-zero value
for PEBS events, perf will _always_ generate an adaptive record, even if
the guest requested a basic record.  Note, KVM will also enable adaptive
PEBS in individual *counter*, even if adaptive PEBS isn't exposed to the
guest, but this is benign as MSR_PEBS_DATA_CFG is guaranteed to be zero,
i.e. the guest will only ever see Basic records.

Bug #3 is in perf.  intel_pmu_disable_fixed() doesn't clear the upper
bits either, i.e. leaves ICL_FIXED_0_ADAPTIVE set, and
intel_pmu_enable_fixed() effectively doesn't clear ICL_FIXED_0_ADAPTIVE
either.  I.e. perf _always_ enables ADAPTIVE counters, regardless of what
KVM requests.

Bug #4 is that adaptive PEBS *might* effectively bypass event filters set
by the host, as "Updated Memory Access Info Group" records information
that might be disallowed by userspace via KVM_SET_PMU_EVENT_FILTER.

Bug #5 is that KVM doesn't ensure LBR MSRs hold guest values (or at least
zeros) when entering a vCPU with adaptive PEBS, which allows the guest
to read host LBRs, i.e. host RIPs/addresses, by enabling "LBR Entries"
records.

Disable adaptive PEBS support as an immediate fix due to the severity of
the LBR leak in particular, and because fixing all of the bugs will be
non-trivial, e.g. not suitable for backporting to stable kernels.

Note!  This will break live migration, but trying to make KVM play nice
with live migration would be quite complicated, wouldn't be guaranteed to
work (i.e. KVM might still kill/confuse the guest), and it's not clear
that there are any publicly available VMMs that support adaptive PEBS,
let alone live migrate VMs that support adaptive PEBS, e.g. QEMU doesn't
support PEBS in any capacity.

## References
- https://git.kernel.org/stable/c/037e48ceccf163899374b601afb6ae8d0bf1d2ac
- https://git.kernel.org/stable/c/0fb74c00d140a66128afc0003785dcc57e69d312
- https://git.kernel.org/stable/c/7a7650b3ac23e5fc8c990f00e94f787dc84e3175
- https://git.kernel.org/stable/c/9e985cbf2942a1bb8fcef9adc2a17d90fd7ca8ee
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EZ6PJW7VOZ224TD7N4JZNU6KV32ZJ53/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DAMSOZXJEPUOXW33WZYWCVAY7Z5S7OOY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GCBZZEC7L7KTWWAS2NLJK6SO3IZIL4WW/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26992.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26992
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
