# [M] pinmux: Use sequential access to access desc->pinmux data

## Summary
Severity: Medium
Advisory: CVE-2024-47141
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-47141
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinmux: Use sequential access to access desc->pinmux data

When two client of the same gpio call pinctrl_select_state() for the
same functionality, we are seeing NULL pointer issue while accessing
desc->mux_owner.

Let's say two processes A, B executing in pin_request() for the same pin
and process A updates the desc->mux_usecount but not yet updated the
desc->mux_owner while process B see the desc->mux_usecount which got
updated by A path and further executes strcmp and while accessing
desc->mux_owner it crashes with NULL pointer.

Serialize the access to mux related setting with a mutex lock.

	cpu0 (process A)			cpu1(process B)

pinctrl_select_state() {		  pinctrl_select_state() {
  pin_request() {				pin_request() {
  ...
						 ....
    } else {
         desc->mux_usecount++;
    						desc->mux_usecount && strcmp(desc->mux_owner, owner)) {

         if (desc->mux_usecount > 1)
               return 0;
         desc->mux_owner = owner;

  }						}

## References
- https://git.kernel.org/stable/c/2da32aed4a97ca1d70fb8b77926f72f30ce5fb4b
- https://git.kernel.org/stable/c/5a3e85c3c397c781393ea5fb2f45b1f60f8a4e6e
- https://git.kernel.org/stable/c/c11e2ec9a780f54982a187ee10ffd1b810715c85
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47141.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47141
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
