# [M] CVE-2020-25427

## Summary
Severity: Medium
Advisory: CVE-2020-25427
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2020-25427
Type: osv

## Details
A Null pointer dereference vulnerability exits in MP4Box - GPAC version 0.8.0-rev177-g51a8ef874-master via the gf_isom_get_track_id function, which causes a denial of service.

## References
- https://github.com/gpac/gpac/issues/1406
- https://github.com/gpac/gpac/commit/8e585e623b1d666b4ef736ed609264639cb27701
