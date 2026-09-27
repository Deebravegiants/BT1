# [H] parport: Fix race between port and client registration

## Summary
Severity: High
Advisory: CVE-2026-63942
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63942
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

parport: Fix race between port and client registration

The parport subsystem registers port devices before they are fully
initialised, resulting in a race condition where client drivers such
as lp can attach to ports that are not completely initialised or even
being torn down.

When the port and client drivers are built as modules and loaded
around the same time during boot, this occasionally results in a
crash.  I was able to make this happen reliably in a VM with a
PC-style parallel port by patching parport_pc to fail probing:

> --- a/drivers/parport/parport_pc.c
> +++ b/drivers/parport/parport_pc.c
> @@ -2069,7 +2069,7 @@ static struct parport *__parport_pc_probe_port(unsigned long int base,
>  	if (!p)
>  		goto out3;
>
> -	base_res = request_region(base, 3, p->name);
> +	base_res = NULL;
>  	if (!base_res)
>  		goto out4;
>

and then running:

    while true; do
        modprobe lp & modprobe parport_pc
	wait
	rmmod lp parport_pc
    done

for a few seconds.

In the long term I think port registration should be changed to put
the call to device_add() inside parport_announce_port(), but since the
latter currently cannot fail this will require changing all port
drivers.

For now, add a flag to indicate whether a port has been "announced"
and only try to attach client drivers to ports when the flag is set.

## References
- https://git.kernel.org/stable/c/15b1723c1472e802f9f7e69ae4e64f7dbf588848
- https://git.kernel.org/stable/c/290f515c5e3b3900bc2fe24f179999fd08d23bfa
- https://git.kernel.org/stable/c/51026cff1f4f3b762a0b5a07c727bd59cef45320
- https://git.kernel.org/stable/c/74d6aae1df45d3414178986be743f946988fddf6
- https://git.kernel.org/stable/c/a1e81b58da0179531bedf0b9f2811f5f992d5c4b
- https://git.kernel.org/stable/c/d16548be2ea5058227d79799e81dab61c9bca8ec
- https://git.kernel.org/stable/c/ef15ccbb3e8640a723c42ad90eaf81d66ae02017
- https://git.kernel.org/stable/c/f3378b0d7bd4605de89b083b2900788157a181cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63942.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63942
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
