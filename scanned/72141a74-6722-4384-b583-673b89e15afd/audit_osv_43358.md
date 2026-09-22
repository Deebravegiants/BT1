# [M] Gstreamer1-plugins-good: gstreamer: out-of-bounds read in avidemux vprp video field descriptor parsing

## Summary
Severity: Medium
Advisory: CVE-2026-73434
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73434
Type: osv

## Details
A flaw was found in GStreamer gst-plugins-good (avidemux). In gst_avi_demux_riff_parse_vprp(), the number of available gst_riff_vprp_video_field_desc entries is calculated by dividing the remaining buffer size by the attacker-controlled vprp->fields value, rather than by sizeof(gst_riff_vprp_video_field_desc). This can cause the parser to treat more field descriptors as available than fit in the input buffer, resulting in out-of-bounds reads. Processing a crafted AVI via playbin/decodebin can crash the application (denial of service). Fixed upstream in gst-plugins-good 1.28.6 (GStreamer-SA-2026-0072).

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://gstreamer.freedesktop.org/security/sa-2026-0072.html
- https://access.redhat.com/errata/RHSA-2026:55434
- https://access.redhat.com/errata/RHSA-2026:55436
- https://access.redhat.com/errata/RHSA-2026:56966
- https://access.redhat.com/errata/RHSA-2026:65959
- https://access.redhat.com/security/cve/CVE-2026-73434
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73434.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73434
- https://bugzilla.redhat.com/show_bug.cgi?id=2514807
- https://gitlab.freedesktop.org/gstreamer/gstreamer/-/merge_requests/12231
- https://gitlab.freedesktop.org/gstreamer/gst-plugins-good
