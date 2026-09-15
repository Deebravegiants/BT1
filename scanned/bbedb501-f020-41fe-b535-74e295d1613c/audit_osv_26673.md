# [H] jbd2: check 'jh->b_transaction' before removing it from checkpoint

## Summary
Severity: High
Advisory: CVE-2023-53526
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53526
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.132, >=5.16.0 <6.1.54, >=6.2.0 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

jbd2: check 'jh->b_transaction' before removing it from checkpoint

Following process will corrupt ext4 image:
Step 1:
jbd2_journal_commit_transaction
 __jbd2_journal_insert_checkpoint(jh, commit_transaction)
 // Put jh into trans1->t_checkpoint_list
 journal->j_checkpoint_transactions = commit_transaction
 // Put trans1 into journal->j_checkpoint_transactions

Step 2:
do_get_write_access
 test_clear_buffer_dirty(bh) // clear buffer dirty，set jbd dirty
 __jbd2_journal_file_buffer(jh, transaction) // jh belongs to trans2

Step 3:
drop_cache
 journal_shrink_one_cp_list
  jbd2_journal_try_remove_checkpoint
   if (!trylock_buffer(bh))  // lock bh, true
   if (buffer_dirty(bh))     // buffer is not dirty
   __jbd2_journal_remove_checkpoint(jh)
   // remove jh from trans1->t_checkpoint_list

Step 4:
jbd2_log_do_checkpoint
 trans1 = journal->j_checkpoint_transactions
 // jh is not in trans1->t_checkpoint_list
 jbd2_cleanup_journal_tail(journal)  // trans1 is done

Step 5: Power cut, trans2 is not committed, jh is lost in next mounting.

Fix it by checking 'jh->b_transaction' before remove it from checkpoint.

## References
- https://git.kernel.org/stable/c/2298f2589903a8bc03061b54b31fd97985ab6529
- https://git.kernel.org/stable/c/590a809ff743e7bd890ba5fb36bc38e20a36de53
- https://git.kernel.org/stable/c/dbafe636db415299e54d9dfefc1003bda9e71c9d
- https://git.kernel.org/stable/c/ef5fea70e5915afd64182d155e72bfb4f275e1fc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53526.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53526
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
