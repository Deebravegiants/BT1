# [M] Gstreamer1-plugins-good: gstreamer: unsigned integer underflow in avidemux fujifilm strd parsing leading to out-of-bounds read/write

## Summary
Severity: Medium
Advisory: CVE-2026-73433
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73433
Type: osv

## Details
A flaw was found in GStreamer gst-plugins-good (avidemux). When parsing FUJIFILM metadata in an AVI strd chunk, gst_avi_demux_parse_strd() decrements a remaining-length counter by fixed offsets (98 and 10 bytes) without verifying sufficient data remains. For crafted strd payloads of exactly 106 or 107 bytes, the counter underflows to a very large unsigned value, causing subsequent null-terminated string scanning to read far beyond the allocated heap buffer. Date-format normalization may also write beyond the buffer end. Confirmed impacts include heap out-of-bounds read, out-of-bounds write, heap information disclosure (adjacent data appearing in parsed metadata), and application crash/denial of service. The avidemux element is auto-plugged by playbin, decodebin, and gst-discoverer, so opening or previewing a crafted AVI is sufficient to trigger the issue. Fixed upstream in gst-plugins-good 1.28.6 (GStreamer-SA-2026-0072).

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://gstreamer.freedesktop.org/security/sa-2026-0072.html
- https://access.redhat.com/errata/RHSA-2026:55434
- https://access.redhat.com/errata/RHSA-2026:55436
- https://access.redhat.com/errata/RHSA-2026:56966
- https://access.redhat.com/errata/RHSA-2026:65959
- https://access.redhat.com/security/cve/CVE-2026-73433
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73433.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73433
- https://bugzilla.redhat.com/show_bug.cgi?id=2514801
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/12231
- https://gitlab.freedesktop.org/gstreamer/gst-plugins-good
