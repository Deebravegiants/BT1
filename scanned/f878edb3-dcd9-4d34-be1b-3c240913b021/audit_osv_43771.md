# [H] hwmon: (pmbus) Fix type confusion in notification logic

## Summary
Severity: High
Advisory: CVE-2026-74711
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74711
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (pmbus) Fix type confusion in notification logic

Sashiko reports:

At the start of the loop in pmbus_notify(), the code unconditionally casts
every attribute to a struct sensor_device_attribute:

drivers/hwmon/pmbus/pmbus_core.c:pmbus_notify() {
    for (i = 0; i < data->num_attributes; i++) {
        struct device_attribute *da = to_dev_attr(data->group.attrs[i]);
        struct sensor_device_attribute *attr = to_sensor_dev_attr(da);
        int index = attr->index;
...
}

However, data->group.attrs can contain other types like struct
pmbus_samples_reg or struct pmbus_sensor, which only embed a base
struct device_attribute.

If da is a struct pmbus_samples_reg, dev_attr is the last member. Casting
it to struct sensor_device_attribute and reading the index field appears
to access memory past the end of the allocation, which might trigger a
slab-out-of-bounds read.

Additionally, if da is a struct pmbus_sensor, casting it causes the index
field to overlap with the page, phase, and reg fields. Could this produce
a garbage mask on little-endian systems that spuriously matches the target
reg, page, and flags during an alert?

Fix the problem by using struct sensor_device_attr in struct pmbus_sensor
and struct pmbus_label. Since those attributes never trigger a
notification, set the value of attr->index to -1 for them. Use this value
to distinguish from boolean attributes which _can_ trigger a notification
and use the index field to encode mask, page, and register values.

## References
- https://git.kernel.org/stable/c/0b121de89a99c54bcf516999b04e8531c84f08d5
- https://git.kernel.org/stable/c/59bd68ab05a8f9c9a60b6ec44682084184803ff4
- https://git.kernel.org/stable/c/821f6416e69782fa662aff94b5ea52c943042790
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74711.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74711
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
