# [H] tracing: Fix bad hist from corrupting named_triggers list

## Summary
Severity: High
Advisory: CVE-2025-21899
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21899
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <6.1.130, >=6.2.0 <6.6.81, >=6.7.0 <6.12.18, >=6.13.0 <6.13.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Fix bad hist from corrupting named_triggers list

The following commands causes a crash:

 ~# cd /sys/kernel/tracing/events/rcu/rcu_callback
 ~# echo 'hist:name=bad:keys=common_pid:onmax(bogus).save(common_pid)' > trigger
 bash: echo: write error: Invalid argument
 ~# echo 'hist:name=bad:keys=common_pid' > trigger

Because the following occurs:

event_trigger_write() {
  trigger_process_regex() {
    event_hist_trigger_parse() {

      data = event_trigger_alloc(..);

      event_trigger_register(.., data) {
        cmd_ops->reg(.., data, ..) [hist_register_trigger()] {
          data->ops->init() [event_hist_trigger_init()] {
            save_named_trigger(name, data) {
              list_add(&data->named_list, &named_triggers);
            }
          }
        }
      }

      ret = create_actions(); (return -EINVAL)
      if (ret)
        goto out_unreg;
[..]
      ret = hist_trigger_enable(data, ...) {
        list_add_tail_rcu(&data->list, &file->triggers); <<<---- SKIPPED!!! (this is important!)
[..]
 out_unreg:
      event_hist_unregister(.., data) {
        cmd_ops->unreg(.., data, ..) [hist_unregister_trigger()] {
          list_for_each_entry(iter, &file->triggers, list) {
            if (!hist_trigger_match(data, iter, named_data, false))   <- never matches
                continue;
            [..]
            test = iter;
          }
          if (test && test->ops->free) <<<-- test is NULL

            test->ops->free(test) [event_hist_trigger_free()] {
              [..]
              if (data->name)
                del_named_trigger(data) {
                  list_del(&data->named_list);  <<<<-- NEVER gets removed!
                }
              }
           }
         }

         [..]
         kfree(data); <<<-- frees item but it is still on list

The next time a hist with name is registered, it causes an u-a-f bug and
the kernel can crash.

Move the code around such that if event_trigger_register() succeeds, the
next thing called is hist_trigger_enable() which adds it to the list.

A bunch of actions is called if get_named_trigger_data() returns false.
But that doesn't need to be called after event_trigger_register(), so it
can be moved up, allowing event_trigger_register() to be called just
before hist_trigger_enable() keeping them together and allowing the
file->triggers to be properly populated.

## References
- https://git.kernel.org/stable/c/435d2964af815aae456db554c62963b4515f19d0
- https://git.kernel.org/stable/c/43b254d46c740bf9dbe65709afa021dd726dfa99
- https://git.kernel.org/stable/c/5ae1b18f05ee2b849dc03b6c15d7da0c1c6efa77
- https://git.kernel.org/stable/c/6f86bdeab633a56d5c6dccf1a2c5989b6a5e323e
- https://git.kernel.org/stable/c/f1ae50cfb818ce1ac7a674406dfadb7653e2552d
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21899.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21899
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
