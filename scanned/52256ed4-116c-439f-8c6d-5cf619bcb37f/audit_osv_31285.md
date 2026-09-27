# [H] Qemu-kvm: virtio-snd: heap buffer overflow in virtio_snd_pcm_in_cb()

## Summary
Severity: High
Advisory: CVE-2024-7730
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/CVE-2024-7730
Type: osv

## Details
A heap buffer overflow was found in the virtio-snd device in QEMU. When reading input audio in the virtio-snd input callback, virtio_snd_pcm_in_cb, the function did not check whether the iov can fit the data buffer. This issue can trigger an out-of-bounds write if the size of the virtio queue element is equal to virtio_snd_pcm_status, which makes the available space for audio data zero.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2024-7730
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7730.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7730
- https://bugzilla.redhat.com/show_bug.cgi?id=2304289
- https://gitlab.com/qemu-project/qemu
