# [H] tracing: Fix reading strings from synthetic events

## Summary
Severity: High
Advisory: CVE-2022-50255
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50255
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Fix reading strings from synthetic events

The follow commands caused a crash:

  # cd /sys/kernel/tracing
  # echo 's:open char file[]' > dynamic_events
  # echo 'hist:keys=common_pid:file=filename:onchange($file).trace(open,$file)' > events/syscalls/sys_enter_openat/trigger'
  # echo 1 > events/synthetic/open/enable

BOOM!

The problem is that the synthetic event field "char file[]" will read
the value given to it as a string without any memory checks to make sure
the address is valid. The above example will pass in the user space
address and the sythetic event code will happily call strlen() on it
and then strscpy() where either one will cause an oops when accessing
user space addresses.

Use the helper functions from trace_kprobe and trace_eprobe that can
read strings safely (and actually succeed when the address is from user
space and the memory is mapped in).

Now the above can show:

     packagekitd-1721    [000] ...2.   104.597170: open: file=/usr/lib/rpm/fileattrs/cmake.attr
    in:imjournal-978     [006] ...2.   104.599642: open: file=/var/lib/rsyslog/imjournal.state.tmp
     packagekitd-1721    [000] ...2.   104.626308: open: file=/usr/lib/rpm/fileattrs/debuginfo.attr

## References
- https://git.kernel.org/stable/c/0934ae9977c27133449b6dd8c6213970e7eece38
- https://git.kernel.org/stable/c/149198d0b884e4606ed1d29b330c70016d878276
- https://git.kernel.org/stable/c/d9c79fbcbdb6cb10c07c85040eaf615180b26c48
- https://git.kernel.org/stable/c/f8bae1853196b52ede50950387f5b48cf83b9815
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50255.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50255
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
