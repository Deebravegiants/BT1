# [H] quota: Fix race of dquot_scan_active() with quota deactivation

## Summary
Severity: High
Advisory: CVE-2026-53050
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53050
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.6.0 <6.12.91, >=6.7.0 <6.18.33, >=6.13.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

quota: Fix race of dquot_scan_active() with quota deactivation

dquot_scan_active() can race with quota deactivation in
quota_release_workfn() like:

  CPU0 (quota_release_workfn)         CPU1 (dquot_scan_active)
  ==============================      ==============================
  spin_lock(&dq_list_lock);
  list_replace_init(
    &releasing_dquots, &rls_head);
    /* dquot X on rls_head,
       dq_count == 0,
       DQ_ACTIVE_B still set */
  spin_unlock(&dq_list_lock);
  synchronize_srcu(&dquot_srcu);
                                      spin_lock(&dq_list_lock);
                                      list_for_each_entry(dquot,
                                          &inuse_list, dq_inuse) {
                                        /* finds dquot X */
                                        dquot_active(X) -> true
                                        atomic_inc(&X->dq_count);
                                      }
                                      spin_unlock(&dq_list_lock);
  spin_lock(&dq_list_lock);
  dquot = list_first_entry(&rls_head);
  WARN_ON_ONCE(atomic_read(&dquot->dq_count));

The problem is not only a cosmetic one as under memory pressure the
caller of dquot_scan_active() can end up working on freed dquot.

Fix the problem by making sure the dquot is removed from releasing list
when we acquire a reference to it.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/2bdc80f4619411e5bd4a3ef23f51e14021ed457c
- https://git.kernel.org/stable/c/61e25f664dc2a08299e07d84c85776abc2350f75
- https://git.kernel.org/stable/c/6678dde265708003c2b42551af4a2e3cb05decd5
- https://git.kernel.org/stable/c/82cbdb4c1ebb5ea7d7bd45c18d3483b5bd32ebc1
- https://git.kernel.org/stable/c/ac8a2e0d287ebf35e5d7e51e260b4e146648ba4a
- https://git.kernel.org/stable/c/e93ab401da4b2e2c1b8ef2424de2f238d51c8b2d
- https://git.kernel.org/stable/c/f9438cb8c8ec3adc84b2b450a3aab0123d074c3b
- https://git.kernel.org/stable/c/fdd424d7c35633ac577fd87d1b043d1b8a6cd350
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53050.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53050
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
