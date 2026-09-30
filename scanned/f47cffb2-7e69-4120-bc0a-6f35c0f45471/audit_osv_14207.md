# [H] CVE-2018-7889

## Summary
Severity: High
Advisory: CVE-2018-7889
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-08
Source: https://osv.dev/vulnerability/CVE-2018-7889
Type: osv

## Details
gui2/viewer/bookmarkmanager.py in Calibre 3.18 calls cPickle.load on imported bookmark data, which allows remote attackers to execute arbitrary code via a crafted .pickle file, as demonstrated by Python code that contains an os.system call.

## References
- https://github.com/kovidgoyal/calibre/commit/aeb5b036a0bf657951756688b3c72bd68b6e4a7d
- https://bugs.launchpad.net/calibre/+bug/1753870
