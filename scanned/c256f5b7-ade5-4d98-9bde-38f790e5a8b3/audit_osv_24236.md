# [H] xfrm: Update ipcomp_scratches with NULL when freed

## Summary
Severity: High
Advisory: CVE-2022-50569
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2022-50569
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.9.331, >=4.10.0 <4.14.296, >=4.15.0 <4.19.262, >=4.20.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: Update ipcomp_scratches with NULL when freed

Currently if ipcomp_alloc_scratches() fails to allocate memory
ipcomp_scratches holds obsolete address. So when we try to free the
percpu scratches using ipcomp_free_scratches() it tries to vfree non
existent vm area. Described below:

static void * __percpu *ipcomp_alloc_scratches(void)
{
        ...
        scratches = alloc_percpu(void *);
        if (!scratches)
                return NULL;
ipcomp_scratches does not know about this allocation failure.
Therefore holding the old obsolete address.
        ...
}

So when we free,

static void ipcomp_free_scratches(void)
{
        ...
        scratches = ipcomp_scratches;
Assigning obsolete address from ipcomp_scratches

        if (!scratches)
                return;

        for_each_possible_cpu(i)
               vfree(*per_cpu_ptr(scratches, i));
Trying to free non existent page, causing warning: trying to vfree
existent vm area.
        ...
}

Fix this breakage by updating ipcomp_scrtches with NULL when scratches
is freed

## References
- https://git.kernel.org/stable/c/03155680191ef0f004b1d6a5714c5b8cd271ab61
- https://git.kernel.org/stable/c/18373ed500f7cd53e24d9b0bd0f1c09d78dba87e
- https://git.kernel.org/stable/c/1e8abde895b3ac6a368cbdb372e8800c49e73a28
- https://git.kernel.org/stable/c/2c19945ce8095d065df550e7fe350cd5cc40c6e6
- https://git.kernel.org/stable/c/8a04d2fc700f717104bfb95b0f6694e448a4537f
- https://git.kernel.org/stable/c/a39f456d62810c0efb43cead22f98d95b53e4b1a
- https://git.kernel.org/stable/c/be81c44242b20fc3bdcc73480ef8aaee56f5d0b6
- https://git.kernel.org/stable/c/debca61df6bc2f65e020656c9c5b878d6b38d30f
- https://git.kernel.org/stable/c/f3bdba4440d82e0da2b1bfc35d3836c8a8e00677
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50569.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50569
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
