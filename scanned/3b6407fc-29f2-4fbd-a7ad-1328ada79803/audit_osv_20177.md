# [C] CVE-2021-31875

## Summary
Severity: Critical
Advisory: CVE-2021-31875
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-29
Source: https://osv.dev/vulnerability/CVE-2021-31875
Type: osv

## Details
In mjs_json.c in Cesanta MongooseOS mJS 1.26, a maliciously formed JSON string can trigger an off-by-one heap-based buffer overflow in mjs_json_parse, which can potentially lead to redirection of control flow. NOTE: the original reporter disputes the significance of this finding because "there isn’t very much of an opportunity to exploit this reliably for an information leak, so there isn’t any real security impact."

## References
- https://github.com/cesanta/mjs/releases/tag/1.26
- https://github.com/418sec/mjs/pull/2
- https://huntr.dev/bounties/1-other-mjs/
