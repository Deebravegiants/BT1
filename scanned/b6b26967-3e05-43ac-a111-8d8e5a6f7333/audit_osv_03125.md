# [H] ALPINE-CVE-2024-4741

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-4741
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-4741
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=0 <3.0.14-r0
- Alpine:v3.18: `openssl` — affected >=0 <3.1.6-r0
- Alpine:v3.19: `openssl` — affected >=0 <3.1.6-r0
- Alpine:v3.20: `openssl` — affected >=0 <3.3.0-r3
- Alpine:v3.21: `openssl` — affected >=0 <3.3.0-r3
- Alpine:v3.22: `openssl` — affected >=0 <3.3.0-r3
- Alpine:v3.23: `openssl` — affected >=0 <3.3.0-r3
- Alpine:v3.24: `openssl` — affected >=0 <3.3.0-r3

## Details
Issue summary: Calling the OpenSSL API function SSL_free_buffers may cause
memory to be accessed that was previously freed in some situations

Impact summary: A use after free can have a range of potential consequences such
as the corruption of valid data, crashes or execution of arbitrary code.
However, only applications that directly call the SSL_free_buffers function are
affected by this issue. Applications that do not call this function are not
vulnerable. Our investigations indicate that this function is rarely used by
applications.

The SSL_free_buffers function is used to free the internal OpenSSL buffer used
when processing an incoming record from the network. The call is only expected
to succeed if the buffer is not currently in use. However, two scenarios have
been identified where the buffer is freed even when still in use.

The first scenario occurs where a record header has been received from the
network and processed by OpenSSL, but the full record body has not yet arrived.
In this case calling SSL_free_buffers will succeed even though a record has only
been partially processed and the buffer is still in use.

The second scenario occurs where a full record containing application data has
been received and processed by OpenSSL but the application has only read part of
this data. Again a call to SSL_free_buffers will succeed even though the buffer
is still in use.

While these scenarios could occur accidentally during normal operation a
malicious attacker could attempt to engineer a stituation where this occurs.
We are not aware of this issue being actively exploited.

The FIPS modules in 3.3, 3.2, 3.1 and 3.0 are not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-4741
