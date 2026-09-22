# [H] SMB send off unrelated memory contents

## Summary
Severity: High
Advisory: CURL-CVE-2015-3237
Aliases: CVE-2015-3237
Published: 2015-06-17
Source: https://osv.dev/vulnerability/CURL-CVE-2015-3237
Type: osv

## Details
libcurl can get tricked by a malicious SMB server to send off data it did not
intend to.

In libcurl's state machine function handling the SMB protocol
(`smb_request_state()`), two length and offset values are extracted from data
that has arrived over the network, and those values are subsequently used to
figure out what data range to send back.

The values are used and trusted without boundary checks and are assumed to be
valid. This allows carefully handcrafted packages to trick libcurl into
responding and sending off data that was not intended. Or crash if the values
cause libcurl to access invalid memory.
