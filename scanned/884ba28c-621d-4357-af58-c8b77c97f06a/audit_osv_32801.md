# [H] net_sched: hfsc: Address reentrant enqueue adding class to eltree twice

## Summary
Severity: High
Advisory: CVE-2025-38001
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-06
Source: https://osv.dev/vulnerability/CVE-2025-38001
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.185, >=5.16.0 <6.1.141, >=6.2.0 <6.6.93, >=6.7.0 <6.12.32, >=6.13.0 <6.14.10, >=6.15.0 <6.15.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

net_sched: hfsc: Address reentrant enqueue adding class to eltree twice

Savino says:
    "We are writing to report that this recent patch
    (141d34391abbb315d68556b7c67ad97885407547) [1]
    can be bypassed, and a UAF can still occur when HFSC is utilized with
    NETEM.

    The patch only checks the cl->cl_nactive field to determine whether
    it is the first insertion or not [2], but this field is only
    incremented by init_vf [3].

    By using HFSC_RSC (which uses init_ed) [4], it is possible to bypass the
    check and insert the class twice in the eltree.
    Under normal conditions, this would lead to an infinite loop in
    hfsc_dequeue for the reasons we already explained in this report [5].

    However, if TBF is added as root qdisc and it is configured with a
    very low rate,
    it can be utilized to prevent packets from being dequeued.
    This behavior can be exploited to perform subsequent insertions in the
    HFSC eltree and cause a UAF."

To fix both the UAF and the infinite loop, with netem as an hfsc child,
check explicitly in hfsc_enqueue whether the class is already in the eltree
whenever the HFSC_RSC flag is set.

[1] https://web.git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=141d34391abbb315d68556b7c67ad97885407547
[2] https://elixir.bootlin.com/linux/v6.15-rc5/source/net/sched/sch_hfsc.c#L1572
[3] https://elixir.bootlin.com/linux/v6.15-rc5/source/net/sched/sch_hfsc.c#L677
[4] https://elixir.bootlin.com/linux/v6.15-rc5/source/net/sched/sch_hfsc.c#L1574
[5] https://lore.kernel.org/netdev/8DuRWwfqjoRDLDmBMlIfbrsZg9Gx50DHJc1ilxsEBNe2D6NMoigR_eIRIG0LOjMc3r10nUUZtArXx4oZBIdUfZQrwjcQhdinnMis_0G7VEk=@willsroot.io/T/#u

## References
- https://git.kernel.org/stable/c/295f7c579b07b5b7cf2dffe485f71cc2f27647cb
- https://git.kernel.org/stable/c/2c928b3a0b04a431ffcd6c8b7d88a267124a3a28
- https://git.kernel.org/stable/c/2f2190ce4ca972051cac6a8d7937448f8cb9673c
- https://git.kernel.org/stable/c/39ed887b1dd2d6b720f87e86692ac3006cc111c8
- https://git.kernel.org/stable/c/4e38eaaabfb7fffbb371a51150203e19eee5d70e
- https://git.kernel.org/stable/c/6672e6c00810056acaac019fe26cdc26fee8a66c
- https://git.kernel.org/stable/c/a0ec22fa20b252edbe070a9de8501eef63c17ef5
- https://git.kernel.org/stable/c/ac9fe7dd8e730a103ae4481147395cc73492d786
- https://git.kernel.org/stable/c/e5bee633cc276410337d54b99f77fbc1ad8801e5
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://syst3mfailure.io/rbtree-family-drama/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38001.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38001
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
