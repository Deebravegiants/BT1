# [M] CVE-2018-14779

## Summary
Severity: Medium
Advisory: CVE-2018-14779
CVSS: 6.8 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-15
Source: https://osv.dev/vulnerability/CVE-2018-14779
Type: osv

## Details
A buffer overflow issue was discovered in the Yubico-Piv 1.5.0 smartcard driver. The file lib/ykpiv.c contains the following code in the function `ykpiv_transfer_data()`: {% highlight c %} if(*out_len + recv_len - 2 > max_out) { fprintf(stderr, "Output buffer to small, wanted to write %lu, max was %lu.", *out_len + recv_len - 2, max_out); } if(out_data) { memcpy(out_data, data, recv_len - 2); out_data += recv_len - 2; *out_len += recv_len - 2; } {% endhighlight %} -- it is clearly checked whether the buffer is big enough to hold the data copied using `memcpy()`, but no error handling happens to avoid the `memcpy()` in such cases. This code path can be triggered with malicious data coming from a smartcard.

## References
- https://usn.ubuntu.com/4276-1/
- http://www.openwall.com/lists/oss-security/2018/08/14/2
- https://www.x41-dsec.de/lab/advisories/x41-2018-001-Yubico-Piv/
- https://www.yubico.com/support/security-advisories/ysa-2018-03/
