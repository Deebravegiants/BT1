# [H] s390/cpum_sf: Handle CPU hotplug remove during sampling

## Summary
Severity: High
Advisory: CVE-2024-57849
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57849
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/cpum_sf: Handle CPU hotplug remove during sampling

CPU hotplug remove handling triggers the following function
call sequence:

   CPUHP_AP_PERF_S390_SF_ONLINE  --> s390_pmu_sf_offline_cpu()
   ...
   CPUHP_AP_PERF_ONLINE          --> perf_event_exit_cpu()

The s390 CPUMF sampling CPU hotplug handler invokes:

 s390_pmu_sf_offline_cpu()
 +-->  cpusf_pmu_setup()
       +--> setup_pmc_cpu()
            +--> deallocate_buffers()

This function de-allocates all sampling data buffers (SDBs) allocated
for that CPU at event initialization. It also clears the
PMU_F_RESERVED bit. The CPU is gone and can not be sampled.

With the event still being active on the removed CPU, the CPU event
hotplug support in kernel performance subsystem triggers the
following function calls on the removed CPU:

  perf_event_exit_cpu()
  +--> perf_event_exit_cpu_context()
       +--> __perf_event_exit_context()
	    +--> __perf_remove_from_context()
	         +--> event_sched_out()
	              +--> cpumsf_pmu_del()
	                   +--> cpumsf_pmu_stop()
                                +--> hw_perf_event_update()

to stop and remove the event. During removal of the event, the
sampling device driver tries to read out the remaining samples from
the sample data buffers (SDBs). But they have already been freed
(and may have been re-assigned). This may lead to a use after free
situation in which case the samples are most likely invalid. In the
best case the memory has not been reassigned and still contains
valid data.

Remedy this situation and check if the CPU is still in reserved
state (bit PMU_F_RESERVED set). In this case the SDBs have not been
released an contain valid data. This is always the case when
the event is removed (and no CPU hotplug off occured).
If the PMU_F_RESERVED bit is not set, the SDB buffers are gone.

## References
- https://git.kernel.org/stable/c/06a92f810df8037ca36157282ddcbefdcaf049b8
- https://git.kernel.org/stable/c/238e3af849dfdcb1faed544349f7025e533f9aab
- https://git.kernel.org/stable/c/99192c735ed4bfdff0d215ec85c8a87a677cb898
- https://git.kernel.org/stable/c/a0bd7dacbd51c632b8e2c0500b479af564afadf3
- https://git.kernel.org/stable/c/a69752f1e5de817941a2ea0609254f6f25acd274
- https://git.kernel.org/stable/c/b5be6a0bb639d165c8418d8dddd8f322587be8be
- https://git.kernel.org/stable/c/be54e6e0f93a39a9c00478d70d12956a5f3d5b9b
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57849.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57849
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
