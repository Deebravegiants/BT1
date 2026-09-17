# [H] CVE-2018-12247

## Summary
Severity: High
Advisory: CVE-2018-12247
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-12
Source: https://osv.dev/vulnerability/CVE-2018-12247
Type: osv

## Details
An issue was discovered in mruby 1.4.1. There is a NULL pointer dereference in mrb_class, related to certain .clone usage, because mrb_obj_clone in kernel.c copies flags other than the MRB_FLAG_IS_FROZEN flag (e.g., the embedded flag).

## References
- https://github.com/mruby/mruby/issues/4036
- https://github.com/mruby/mruby/commit/55edae0226409de25e59922807cb09acb45731a2
