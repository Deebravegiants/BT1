# [H] pstore/ram: fix buffer overflow in persistent_ram_save_old()

## Summary
Severity: High
Advisory: CVE-2026-46253
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-46253
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

pstore/ram: fix buffer overflow in persistent_ram_save_old()

persistent_ram_save_old() can be called multiple times for the same
persistent_ram_zone (e.g., via ramoops_pstore_read -> ramoops_get_next_prz
for PSTORE_TYPE_DMESG records).

Currently, the function only allocates prz->old_log when it is NULL,
but it unconditionally updates prz->old_log_size to the current buffer
size and then performs memcpy_fromio() using this new size. If the
buffer size has grown since the first allocation (which can happen
across different kernel boot cycles), this leads to:

1. A heap buffer overflow (OOB write) in the memcpy_fromio() calls
2. A subsequent OOB read when ramoops_pstore_read() accesses the buffer
   using the incorrect (larger) old_log_size

The KASAN splat would look similar to:
  BUG: KASAN: slab-out-of-bounds in ramoops_pstore_read+0x...
  Read of size N at addr ... by task ...

The conditions are likely extremely hard to hit:

  0. Crash with a ramoops write of less-than-record-max-size bytes.
  1. Reboot: ramoops registers, pstore_get_records(0) reads old crash,
     allocates old_log with size X
  2. Crash handler registered, timer started (if pstore_update_ms >= 0)
  3. Oops happens (non-fatal, system continues)
  4. pstore_dump() writes oops via ramoops_pstore_write() size Y (>X)
  5. pstore_new_entry = 1, pstore_timer_kick() called
  6. System continues running (not a panic oops)
  7. Timer fires after pstore_update_ms milliseconds
  8. pstore_timefunc() → schedule_work() → pstore_dowork() → pstore_get_records(1)
  9. ramoops_get_next_prz() → persistent_ram_save_old()
 10. buffer_size() returns Y, but old_log is X bytes
 11. Y > X: memcpy_fromio() overflows heap

  Requirements:
  - a prior crash record exists that did not fill the record size
    (almost impossible since the crash handler writes as much as it
    can possibly fit into the record, capped by max record size and
    the kmsg buffer almost always exceeds the max record size)
  - pstore_update_ms >= 0 (disabled by default)
  - Non-fatal oops (system survives)

Free and reallocate the buffer when the new size differs from the
previously allocated size. This ensures old_log always has sufficient
space for the data being copied.

## References
- https://git.kernel.org/stable/c/06d2c8bd108cea503f6f6e13e47495ed1085275f
- https://git.kernel.org/stable/c/2fa9a047c6a50ec80c3890dd623b85e237f0d1fd
- https://git.kernel.org/stable/c/4f73486ca822305c1cf5b8ebc0b53a6ab3801a81
- https://git.kernel.org/stable/c/5669645c052f235726a85f443769b6fc02f66762
- https://git.kernel.org/stable/c/58bda5a1d1ee98254383ef34f76b2c35140513ea
- https://git.kernel.org/stable/c/7cfe964e61c0ab667abd5f5b68e0acbf783efa4f
- https://git.kernel.org/stable/c/9a6fc69a570c0780834246d52c856cc3dbc2605f
- https://git.kernel.org/stable/c/cff0ef043e16feb5a02307c8f9d0117a96c5587c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46253.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46253
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
