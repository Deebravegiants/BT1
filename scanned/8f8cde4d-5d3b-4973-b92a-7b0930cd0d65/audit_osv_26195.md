# [H] HID: logitech-hidpp: Fix kernel crash on receiver USB disconnect

## Summary
Severity: High
Advisory: CVE-2023-52478
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2023-52478
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <4.14.328, >=4.15.0 <4.19.297, >=4.20.0 <5.4.259, >=5.5.0 <5.10.199, >=5.11.0 <5.15.136, >=5.16.0 <6.1.59, >=6.2.0 <6.5.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: logitech-hidpp: Fix kernel crash on receiver USB disconnect

hidpp_connect_event() has *four* time-of-check vs time-of-use (TOCTOU)
races when it races with itself.

hidpp_connect_event() primarily runs from a workqueue but it also runs
on probe() and if a "device-connected" packet is received by the hw
when the thread running hidpp_connect_event() from probe() is waiting on
the hw, then a second thread running hidpp_connect_event() will be
started from the workqueue.

This opens the following races (note the below code is simplified):

1. Retrieving + printing the protocol (harmless race):

	if (!hidpp->protocol_major) {
		hidpp_root_get_protocol_version()
		hidpp->protocol_major = response.rap.params[0];
	}

We can actually see this race hit in the dmesg in the abrt output
attached to rhbz#2227968:

[ 3064.624215] logitech-hidpp-device 0003:046D:4071.0049: HID++ 4.5 device connected.
[ 3064.658184] logitech-hidpp-device 0003:046D:4071.0049: HID++ 4.5 device connected.

Testing with extra logging added has shown that after this the 2 threads
take turn grabbing the hw access mutex (send_mutex) so they ping-pong
through all the other TOCTOU cases managing to hit all of them:

2. Updating the name to the HIDPP name (harmless race):

	if (hidpp->name == hdev->name) {
		...
		hidpp->name = new_name;
	}

3. Initializing the power_supply class for the battery (problematic!):

hidpp_initialize_battery()
{
        if (hidpp->battery.ps)
                return 0;

	probe_battery(); /* Blocks, threads take turns executing this */

	hidpp->battery.desc.properties =
		devm_kmemdup(dev, hidpp_battery_props, cnt, GFP_KERNEL);

	hidpp->battery.ps =
		devm_power_supply_register(&hidpp->hid_dev->dev,
					   &hidpp->battery.desc, cfg);
}

4. Creating delayed input_device (potentially problematic):

	if (hidpp->delayed_input)
		return;

	hidpp->delayed_input = hidpp_allocate_input(hdev);

The really big problem here is 3. Hitting the race leads to the following
sequence:

	hidpp->battery.desc.properties =
		devm_kmemdup(dev, hidpp_battery_props, cnt, GFP_KERNEL);

	hidpp->battery.ps =
		devm_power_supply_register(&hidpp->hid_dev->dev,
					   &hidpp->battery.desc, cfg);

	...

	hidpp->battery.desc.properties =
		devm_kmemdup(dev, hidpp_battery_props, cnt, GFP_KERNEL);

	hidpp->battery.ps =
		devm_power_supply_register(&hidpp->hid_dev->dev,
					   &hidpp->battery.desc, cfg);

So now we have registered 2 power supplies for the same battery,
which looks a bit weird from userspace's pov but this is not even
the really big problem.

Notice how:

1. This is all devm-maganaged
2. The hidpp->battery.desc struct is shared between the 2 power supplies
3. hidpp->battery.desc.properties points to the result from the second
   devm_kmemdup()

This causes a use after free scenario on USB disconnect of the receiver:
1. The last registered power supply class device gets unregistered
2. The memory from the last devm_kmemdup() call gets freed,
   hidpp->battery.desc.properties now points to freed memory
3. The first registered power supply class device gets unregistered,
   this involves sending a remove uevent to userspace which invokes
   power_supply_uevent() to fill the uevent data
4. power_supply_uevent() uses hidpp->battery.desc.properties which
   now points to freed memory leading to backtraces like this one:

Sep 22 20:01:35 eric kernel: BUG: unable to handle page fault for address: ffffb2140e017f08
...
Sep 22 20:01:35 eric kernel: Workqueue: usb_hub_wq hub_event
Sep 22 20:01:35 eric kernel: RIP: 0010:power_supply_uevent+0xee/0x1d0
...
Sep 22 20:01:35 eric kernel:  ? asm_exc_page_fault+0x26/0x30
Sep 22 20:01:35 eric kernel:  ? power_supply_uevent+0xee/0x1d0
Sep 22 20:01:35 eric kernel:  ? power_supply_uevent+0x10d/0x1d0
Sep 22 20:01:35 eric kernel:  dev_uevent+0x10f/0x2d0
Sep 22 20:01:35 eric kernel:  kobject_uevent_env+0x291/0x680
Sep 22 20:01:35 eric kernel:  
---truncated---

## References
- https://git.kernel.org/stable/c/093af62c023537f097d2ebdfaa0bc7c1a6e874e1
- https://git.kernel.org/stable/c/28ddc1e0b898291323b62d770b1b931de131a528
- https://git.kernel.org/stable/c/44481b244fcaa2b895a53081d6204c574720c38c
- https://git.kernel.org/stable/c/ca0c4cc1d215dc22ab0e738c9f017c650f3183f5
- https://git.kernel.org/stable/c/cd0e2bf7fb22fe9b989c59c42dca06367fd10e6b
- https://git.kernel.org/stable/c/dac501397b9d81e4782232c39f94f4307b137452
- https://git.kernel.org/stable/c/f7b2c7d9831af99369fe8ad9b2a68d78942f414e
- https://git.kernel.org/stable/c/fd72ac9556a473fc7daf54efb6ca8a97180d621d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52478.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52478
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
