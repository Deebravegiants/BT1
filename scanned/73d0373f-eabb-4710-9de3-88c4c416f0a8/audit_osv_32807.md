# [H] HID: bpf: abort dispatch if device destroyed

## Summary
Severity: High
Advisory: CVE-2025-38016
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38016
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.30, >=6.13.0 <6.14.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: bpf: abort dispatch if device destroyed

The current HID bpf implementation assumes no output report/request will
go through it after hid_bpf_destroy_device() has been called. This leads
to a bug that unplugging certain types of HID devices causes a cleaned-
up SRCU to be accessed. The bug was previously a hidden failure until a
recent x86 percpu change [1] made it access not-present pages.

The bug will be triggered if the conditions below are met:

A) a device under the driver has some LEDs on
B) hid_ll_driver->request() is uninplemented (e.g., logitech-djreceiver)

If condition A is met, hidinput_led_worker() is always scheduled *after*
hid_bpf_destroy_device().

hid_destroy_device
` hid_bpf_destroy_device
  ` cleanup_srcu_struct(&hdev->bpf.srcu)
` hid_remove_device
  ` ...
    ` led_classdev_unregister
      ` led_trigger_set(led_cdev, NULL)
        ` led_set_brightness(led_cdev, LED_OFF)
          ` ...
            ` input_inject_event
              ` input_event_dispose
                ` hidinput_input_event
                  ` schedule_work(&hid->led_work) [hidinput_led_worker]

This is fine when condition B is not met, where hidinput_led_worker()
calls hid_ll_driver->request(). This is the case for most HID drivers,
which implement it or use the generic one from usbhid. The driver itself
or an underlying driver will then abort processing the request.

Otherwise, hidinput_led_worker() tries hid_hw_output_report() and leads
to the bug.

hidinput_led_worker
` hid_hw_output_report
  ` dispatch_hid_bpf_output_report
    ` srcu_read_lock(&hdev->bpf.srcu)
    ` srcu_read_unlock(&hdev->bpf.srcu, idx)

The bug has existed since the introduction [2] of
dispatch_hid_bpf_output_report(). However, the same bug also exists in
dispatch_hid_bpf_raw_requests(), and I've reproduced (no visible effect
because of the lack of [1], but confirmed bpf.destroyed == 1) the bug
against the commit (i.e., the Fixes:) introducing the function. This is
because hidinput_led_worker() falls back to hid_hw_raw_request() when
hid_ll_driver->output_report() is uninplemented (e.g., logitech-
djreceiver).

hidinput_led_worker
` hid_hw_output_report: -ENOSYS
` hid_hw_raw_request
  ` dispatch_hid_bpf_raw_requests
    ` srcu_read_lock(&hdev->bpf.srcu)
    ` srcu_read_unlock(&hdev->bpf.srcu, idx)

Fix the issue by returning early in the two mentioned functions if
hid_bpf has been marked as destroyed. Though
dispatch_hid_bpf_device_event() handles input events, and there is no
evidence that it may be called after the destruction, the same check, as
a safety net, is also added to it to maintain the consistency among all
dispatch functions.

The impact of the bug on other architectures is unclear. Even if it acts
as a hidden failure, this is still dangerous because it corrupts
whatever is on the address calculated by SRCU. Thus, CC'ing the stable
list.

[1]: commit 9d7de2aa8b41 ("x86/percpu/64: Use relative percpu offsets")
[2]: commit 9286675a2aed ("HID: bpf: add HID-BPF hooks for
hid_hw_output_report")

## References
- https://git.kernel.org/stable/c/578e1b96fad7402ff7e9c7648c8f1ad0225147c8
- https://git.kernel.org/stable/c/e4b4fe25a4101d1ddb5884f40e149a3618983b66
- https://git.kernel.org/stable/c/f8544be7e8e55b0ef23e1ab90e23e8d4d4aad3d3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38016.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38016
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
