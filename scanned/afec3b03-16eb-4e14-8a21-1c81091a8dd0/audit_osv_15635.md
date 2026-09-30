# [H] CVE-2019-18214

## Summary
Severity: High
Advisory: CVE-2019-18214
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2019-10-19
Source: https://osv.dev/vulnerability/CVE-2019-18214
Type: osv

## Details
The Video_Converter app 0.1.0 for Nextcloud allows denial of service (CPU and memory consumption) via multiple concurrent conversions because many FFmpeg processes may be running at once. (The workload is not queued for serial execution.)

## References
- https://github.com/PaulLereverend/NextcloudVideo_Converter/issues/22
