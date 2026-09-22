# [H] ALPINE-CVE-2019-18397

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18397
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18397
Type: osv

## Affected
- Alpine:v3.10: `fribidi` — affected >=1.0.0 <1.0.5-r2
- Alpine:v3.11: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.12: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.13: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.14: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.15: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.16: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.17: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.18: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.19: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.20: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.21: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.22: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.23: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.24: `fribidi` — affected >=1.0.0 <1.0.7-r1
- Alpine:v3.8: `fribidi` — affected >=1.0.0 <1.0.2-r1
- Alpine:v3.9: `fribidi` — affected >=1.0.0 <1.0.5-r1

## Details
A buffer overflow in the fribidi_get_par_embedding_levels_ex() function in lib/fribidi-bidi.c of GNU FriBidi through 1.0.7 allows an attacker to cause a denial of service or possibly execute arbitrary code by delivering crafted text content to a user, when this content is then rendered by an application that uses FriBidi for text layout calculations. Examples include any GNOME or GTK+ based application that uses Pango for text layout, as this internally uses FriBidi for bidirectional text layout. For example, the attacker can construct a crafted text file to be opened in GEdit, or a crafted IRC message to be viewed in HexChat.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18397
