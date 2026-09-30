# [C] CVE-2019-19307

## Summary
Severity: Critical
Advisory: CVE-2019-19307
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-19307
Type: osv

## Details
An integer overflow in parse_mqtt in mongoose.c in Cesanta Mongoose 6.16 allows an attacker to achieve remote DoS (infinite loop), or possibly cause an out-of-bounds write, by sending a crafted MQTT protocol packet.

## References
- https://github.com/cesanta/mongoose/issues/1055
