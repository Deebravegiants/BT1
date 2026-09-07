# [?] http: fix Sec-WebSocket-Key decode stack overflow (#10142)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-06-09
Source: https://github.com/firedancer-io/firedancer/commit/a4795c54fd0794cb4ae6274b1bbf111246f243b1
Type: security-commit

## Details
http: fix Sec-WebSocket-Key decode stack overflow (#10142)

decoded_key was sized 16 bytes, but fd_base64_decode writes up to
FD_BASE64_DEC_SZ(24)==18 bytes before returning the length we check.
An unpadded 24 char key decodes to 18 bytes, overflowing the stack
by 2 attacker-controlled bytes.  Size the buffer to the decoder's
max output and make test_ws_bad_key_close actually reach the decode.
