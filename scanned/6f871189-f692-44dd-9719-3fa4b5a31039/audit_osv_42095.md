# [H] iio: adc: ad_sigma_delta: fix clear_pending_event for registerless devices

## Summary
Severity: High
Advisory: CVE-2026-64502
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64502
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: adc: ad_sigma_delta: fix clear_pending_event for registerless devices

ad_sigma_delta_clear_pending_event() falls through to the status register
read path for devices with has_registers = false and no rdy_gpiod. For
such devices, ad_sd_read_reg() skips the address byte entirely and clocks
raw MISO bytes with no address phase — making it byte-for-byte identical
to reading conversion data. If a pending conversion result is present,
this partially consumes it and corrupts the data stream for the subsequent
ad_sd_read_reg() call in ad_sigma_delta_single_conversion().

Furthermore, with num_resetclks = 0 on these devices, data_read_len
evaluates to 0. If the clocked byte has bit 7 clear, pending_event is set
and the code attempts memset(data + 2, 0xff, 0 - 1), overflowing to
SIZE_MAX and corrupting the heap.

Fix by returning 0 immediately when neither rdy_gpiod nor has_registers
is set. This is safe for all current registerless devices: ad7191 and
ad7780 (with powerdown GPIO) are reset between conversions by CS
deassertion, so there is no stale result to drain; ad7780 (without
powerdown GPIO) and max11205 are continuously-converting and cycle ~DRDY
at the output data rate regardless of whether the previous result was
read, so the next falling edge fires naturally.

A future registerless device that holds ~DRDY asserted until data is read
would be broken by this early return and would require either
num_resetclks set or a rdy-gpio.

The same heap corruption is reachable on any device with rdy_gpiod set
but num_resetclks = 0: if the GPIO indicates a pending event, the drain
path executes memset(data + 2, 0xff, 0 - 1) regardless of has_registers.
Add an explicit data_read_len == 0 guard after the pending event check;
the stale result is then consumed by the first ad_sd_read_reg() call in
ad_sigma_delta_single_conversion().

## References
- https://git.kernel.org/stable/c/3394e0b3328422431cadaf314fa58d3717ed4936
- https://git.kernel.org/stable/c/3bceb26dfaf7ba805b459e41c1d0ba916862dade
- https://git.kernel.org/stable/c/91bc6767a4f55dc470d8a56b55b9f2ea09094efe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64502.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64502
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
