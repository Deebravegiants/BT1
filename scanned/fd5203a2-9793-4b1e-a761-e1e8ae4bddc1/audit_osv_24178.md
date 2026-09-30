# [M] padata: Always leave BHs disabled when running ->parallel()

## Summary
Severity: Medium
Advisory: CVE-2022-50382
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50382
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

padata: Always leave BHs disabled when running ->parallel()

A deadlock can happen when an overloaded system runs ->parallel() in the
context of the current task:

    padata_do_parallel
      ->parallel()
        pcrypt_aead_enc/dec
          padata_do_serial
            spin_lock(&reorder->lock) // BHs still enabled
              <interrupt>
                ...
                  __do_softirq
                    ...
                      padata_do_serial
                        spin_lock(&reorder->lock)

It's a bug for BHs to be on in _do_serial as Steffen points out, so
ensure they're off in the "current task" case like they are in
padata_parallel_worker to avoid this situation.

## References
- https://git.kernel.org/stable/c/17afa98bccec4f52203508b3f49b5f948c6fd6ac
- https://git.kernel.org/stable/c/34c3a47d20ae55b3600fed733bf96eafe9c500d5
- https://git.kernel.org/stable/c/6cfa9e60c0f88fdec6368e081ab968411cc706b1
- https://git.kernel.org/stable/c/7337adb20fcc0aebb50eaff2bc5a8dd9a7c6743d
- https://git.kernel.org/stable/c/8e0681dd4eee029eb1d533d06993f7cb091efb73
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50382.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50382
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
