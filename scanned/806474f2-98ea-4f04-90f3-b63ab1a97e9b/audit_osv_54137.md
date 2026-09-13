# [M] CVE-2023-39562

## Summary
Severity: Medium
Advisory: CVE-2023-39562
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-28
Source: https://osv.dev/vulnerability/CVE-2023-39562
Type: osv

## Details
GPAC v2.3-DEV-rev449-g5948e4f70-master was discovered to contain a heap-use-after-free via the gf_bs_align function at bitstream.c. This vulnerability allows attackers to cause a Denial of Service (DoS) via supplying a crafted file.

## References
- https://github.com/ChanStormstout/Pocs/blob/master/gpac_POC/id%3A000000%2Csig%3A06%2Csrc%3A003771%2Ctime%3A328254%2Cexecs%3A120473%2Cop%3Ahavoc%2Crep%3A8
- https://github.com/gpac/gpac/issues/2537
