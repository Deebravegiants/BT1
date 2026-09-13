# [H] iommufd: Use sizeof(*hdr) instead of sizeof(hdr) in veventq read

## Summary
Severity: High
Advisory: CVE-2026-64293
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64293
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommufd: Use sizeof(*hdr) instead of sizeof(hdr) in veventq read

The bound-check in iommufd_veventq_fops_read() for the normal vEVENT
path uses sizeof(hdr) where the surrounding code uses sizeof(*hdr):

	if (!vevent_for_lost_events_header(cur) &&
	    sizeof(hdr) + cur->data_len > count - done) {

hdr is declared as struct iommufd_vevent_header *, so sizeof(hdr)
evaluates to the size of the pointer.  Surrounding code uses
sizeof(*hdr) consistently:

	if (done >= count || sizeof(*hdr) > count - done) {
	...
	if (copy_to_user(buf + done, hdr, sizeof(*hdr))) {
	...
	done += sizeof(*hdr);

struct iommufd_vevent_header is currently 8 bytes (two __u32 fields,
flags and sequence), so on 64-bit (sizeof(void *) == 8) the two
expressions happen to be equal and the check works as intended.

On 32-bit (sizeof(void *) == 4) the check under-counts the header by
4 bytes: a vEVENT whose data_len causes 8 + cur->data_len to exceed
count - done while 4 + cur->data_len does not will pass the check,
then the loop will copy_to_user 8 bytes of header followed by data_len
bytes of payload, writing past the user-supplied buffer.

It is also a latent bug for any future expansion of struct
iommufd_vevent_header beyond sizeof(void *) on 64-bit; the check
should not depend on the type happening to match the host pointer
width.

Use sizeof(*hdr) to match the rest of the function and the actual
amount that will be copied.

## References
- https://git.kernel.org/stable/c/04a177f91160ee18da98f5689482cf0f589ec869
- https://git.kernel.org/stable/c/0cdbb97a4dbd69abdd2ab998b4fbc7803d4b0b72
- https://git.kernel.org/stable/c/be93d186ae88a92e7aa77e122d4e661fa57b1e39
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64293.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64293
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
