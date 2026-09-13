# [H] fs/proc: fix uaf in proc_readdir_de()

## Summary
Severity: High
Advisory: CVE-2025-40271
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-06
Source: https://osv.dev/vulnerability/CVE-2025-40271
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <5.4.302, >=5.5.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.59, >=6.13.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/proc: fix uaf in proc_readdir_de()

Pde is erased from subdir rbtree through rb_erase(), but not set the node
to EMPTY, which may result in uaf access.  We should use RB_CLEAR_NODE()
set the erased node to EMPTY, then pde_subdir_next() will return NULL to
avoid uaf access.

We found an uaf issue while using stress-ng testing, need to run testcase
getdent and tun in the same time.  The steps of the issue is as follows:

1) use getdent to traverse dir /proc/pid/net/dev_snmp6/, and current
   pde is tun3;

2) in the [time windows] unregister netdevice tun3 and tun2, and erase
   them from rbtree.  erase tun3 first, and then erase tun2.  the
   pde(tun2) will be released to slab;

3) continue to getdent process, then pde_subdir_next() will return
   pde(tun2) which is released, it will case uaf access.

CPU 0                                      |    CPU 1
-------------------------------------------------------------------------
traverse dir /proc/pid/net/dev_snmp6/      |   unregister_netdevice(tun->dev)   //tun3 tun2
sys_getdents64()                           |
  iterate_dir()                            |
    proc_readdir()                         |
      proc_readdir_de()                    |     snmp6_unregister_dev()
        pde_get(de);                       |       proc_remove()
        read_unlock(&proc_subdir_lock);    |         remove_proc_subtree()
                                           |           write_lock(&proc_subdir_lock);
        [time window]                      |           rb_erase(&root->subdir_node, &parent->subdir);
                                           |           write_unlock(&proc_subdir_lock);
        read_lock(&proc_subdir_lock);      |
        next = pde_subdir_next(de);        |
        pde_put(de);                       |
        de = next;    //UAF                |

rbtree of dev_snmp6
                        |
                    pde(tun3)
                     /    \
                  NULL  pde(tun2)

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://git.kernel.org/stable/c/03de7ff197a3d0e17d0d5c58fdac99a63cba8110
- https://git.kernel.org/stable/c/1d1596d68a6f11d28f677eedf6cf5b17dbfeb491
- https://git.kernel.org/stable/c/4cba73c4c89219beef7685a47374bf88b1022369
- https://git.kernel.org/stable/c/623bb26127fb581a741e880e1e1a47d79aecb6f8
- https://git.kernel.org/stable/c/67272c11f379d9aa5e0f6b16286b9d89b3f76046
- https://git.kernel.org/stable/c/6f2482745e510ae1dacc9b090194b9c5f918d774
- https://git.kernel.org/stable/c/895b4c0c79b092d732544011c3cecaf7322c36a1
- https://git.kernel.org/stable/c/c81d0385500446efe48c305bbb83d47f2ae23a50
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40271.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40271
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
