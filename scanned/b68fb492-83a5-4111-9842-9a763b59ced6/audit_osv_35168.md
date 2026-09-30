# [H] hfsplus: fix missing hfs_bnode_get() in __hfs_bnode_create

## Summary
Severity: High
Advisory: CVE-2025-68774
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68774
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

hfsplus: fix missing hfs_bnode_get() in __hfs_bnode_create

When sync() and link() are called concurrently, both threads may
enter hfs_bnode_find() without finding the node in the hash table
and proceed to create it.

Thread A:
  hfsplus_write_inode()
    -> hfsplus_write_system_inode()
      -> hfs_btree_write()
        -> hfs_bnode_find(tree, 0)
          -> __hfs_bnode_create(tree, 0)

Thread B:
  hfsplus_create_cat()
    -> hfs_brec_insert()
      -> hfs_bnode_split()
        -> hfs_bmap_alloc()
          -> hfs_bnode_find(tree, 0)
            -> __hfs_bnode_create(tree, 0)

In this case, thread A creates the bnode, sets refcnt=1, and hashes it.
Thread B also tries to create the same bnode, notices it has already
been inserted, drops its own instance, and uses the hashed one without
getting the node.

```

	node2 = hfs_bnode_findhash(tree, cnid);
	if (!node2) {                                 <- Thread A
		hash = hfs_bnode_hash(cnid);
		node->next_hash = tree->node_hash[hash];
		tree->node_hash[hash] = node;
		tree->node_hash_cnt++;
	} else {                                      <- Thread B
		spin_unlock(&tree->hash_lock);
		kfree(node);
		wait_event(node2->lock_wq,
			!test_bit(HFS_BNODE_NEW, &node2->flags));
		return node2;
	}
```

However, hfs_bnode_find() requires each call to take a reference.
Here both threads end up setting refcnt=1. When they later put the node,
this triggers:

BUG_ON(!atomic_read(&node->refcnt))

In this scenario, Thread B in fact finds the node in the hash table
rather than creating a new one, and thus must take a reference.

Fix this by calling hfs_bnode_get() when reusing a bnode newly created by
another thread to ensure the refcount is updated correctly.

A similar bug was fixed in HFS long ago in commit
a9dc087fd3c4 ("fix missing hfs_bnode_get() in __hfs_bnode_create")
but the same issue remained in HFS+ until now.

## References
- https://git.kernel.org/stable/c/152af114287851583cf7e0abc10129941f19466a
- https://git.kernel.org/stable/c/39e149d58ef4d7883cbf87448d39d51292fd342d
- https://git.kernel.org/stable/c/3b0fc7af50b896d0f3d104e70787ba1973bc0b56
- https://git.kernel.org/stable/c/457f795e7abd7770de10216d7f9994a3f12a56d6
- https://git.kernel.org/stable/c/5882e7c8cdbb5e254a69628b780acff89c78071e
- https://git.kernel.org/stable/c/b68dc4134b18a3922cd33439ec614aad4172bc86
- https://git.kernel.org/stable/c/b9d1c6bb5f19460074ce9862cb80be86b5fb0a50
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68774.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68774
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
