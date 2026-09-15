# [M] CVE-2021-47585

## Summary
Severity: Medium
Advisory: CVE-2021-47585
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47585
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix memory leak in __add_inode_ref()

Line 1169 (#3) allocates a memory chunk for victim_name by kmalloc(),
but  when the function returns in line 1184 (#4) victim_name allocated
by line 1169 (#3) is not freed, which will lead to a memory leak.
There is a similar snippet of code in this function as allocating a memory
chunk for victim_name in line 1104 (#1) as well as releasing the memory
in line 1116 (#2).

We should kfree() victim_name when the return value of backref_in_log()
is less than zero and before the function returns in line 1184 (#4).

1057 static inline int __add_inode_ref(struct btrfs_trans_handle *trans,
1058 				  struct btrfs_root *root,
1059 				  struct btrfs_path *path,
1060 				  struct btrfs_root *log_root,
1061 				  struct btrfs_inode *dir,
1062 				  struct btrfs_inode *inode,
1063 				  u64 inode_objectid, u64 parent_objectid,
1064 				  u64 ref_index, char *name, int namelen,
1065 				  int *search_done)
1066 {

1104 	victim_name = kmalloc(victim_name_len, GFP_NOFS);
	// #1: kmalloc (victim_name-1)
1105 	if (!victim_name)
1106 		return -ENOMEM;

1112	ret = backref_in_log(log_root, &search_key,
1113			parent_objectid, victim_name,
1114			victim_name_len);
1115	if (ret < 0) {
1116		kfree(victim_name); // #2: kfree (victim_name-1)
1117		return ret;
1118	} else if (!ret) {

1169 	victim_name = kmalloc(victim_name_len, GFP_NOFS);
	// #3: kmalloc (victim_name-2)
1170 	if (!victim_name)
1171 		return -ENOMEM;

1180 	ret = backref_in_log(log_root, &search_key,
1181 			parent_objectid, victim_name,
1182 			victim_name_len);
1183 	if (ret < 0) {
1184 		return ret; // #4: missing kfree (victim_name-2)
1185 	} else if (!ret) {

1241 	return 0;
1242 }

## References
- https://git.kernel.org/stable/c/493ff661d434d6bdf02e3a21adae04d7a0b4265d
- https://git.kernel.org/stable/c/f35838a6930296fc1988764cfa54cb3f705c0665
- https://git.kernel.org/stable/c/005d9292b5b2e71a009f911bd85d755009b37242
