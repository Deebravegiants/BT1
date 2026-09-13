# [M] CVE-2015-8615

## Summary
Severity: Medium
Advisory: CVE-2015-8615
CVSS: 5.0 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:L)
Published: 2016-01-08
Source: https://osv.dev/vulnerability/CVE-2015-8615
Type: osv

## Details
The hvm_set_callback_via function in arch/x86/hvm/irq.c in Xen 4.6 does not limit the number of printk console messages when logging the new callback method, which allows local HVM guest OS users to cause a denial of service via a large number of changes to the callback method (HVM_PARAM_CALLBACK_IRQ).

## References
- http://xenbits.xen.org/xsa/advisory-169.html
- http://www.securityfocus.com/bid/79644
- http://www.securitytracker.com/id/1034512
