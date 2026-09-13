# [M] JLSEC-2026-642

## Summary
Severity: Medium
Advisory: JLSEC-2026-642
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/JLSEC-2026-642
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=6.1.1+0 <8.1.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <8.1.0+0
- Julia: `FFplay_jll` — affected >=7.1.0+0 <8.1.2+0

## Details
A flaw was found in FFmpeg’s TensorFlow backend within the `libavfilter/dnn_backend_tf.c` source file. The issue occurs in the `dnn_execute_model_tf()` function, where a task object is freed multiple times in certain error-handling paths. This redundant memory deallocation can lead to a double-free condition, potentially causing FFmpeg or any application using it to crash when processing TensorFlow-based DNN models. This results in a denial-of-service scenario but does not allow arbitrary code execution under normal conditions.

## References
- https://access.redhat.com/security/cve/CVE-2025-12343
- https://bugzilla.redhat.com/show_bug.cgi?id=2406533
