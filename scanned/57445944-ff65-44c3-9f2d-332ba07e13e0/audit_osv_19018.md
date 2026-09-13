# [H] CVE-2020-6095

## Summary
Severity: High
Advisory: CVE-2020-6095
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-27
Source: https://osv.dev/vulnerability/CVE-2020-6095
Type: osv

## Details
An exploitable denial of service vulnerability exists in the GstRTSPAuth functionality of GStreamer/gst-rtsp-server 1.14.5. A specially crafted RTSP setup request can cause a null pointer deference resulting in denial-of-service. An attacker can send a malicious packet to trigger this vulnerability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00029.html
- https://security.gentoo.org/glsa/202009-05
- https://gitlab.freedesktop.org/gstreamer/gst-rtsp-server/-/commit/44ccca3086dd81081d72ca0b21d0ecdde962fb1a
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2020-1018
