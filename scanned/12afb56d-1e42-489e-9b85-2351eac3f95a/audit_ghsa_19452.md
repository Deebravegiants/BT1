# [H] Data exposure via ZeroMQ on multi-node vLLM deployment

## Summary
Severity: High
Advisory: GHSA-9f8f-2vmf-885j
CVE: CVE-2025-30202
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-29
Source: https://github.com/advisories/GHSA-9f8f-2vmf-885j
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.5.2 <0.8.5

## Details
### Impact
In a multi-node vLLM deployment, vLLM uses ZeroMQ for some multi-node communication purposes. The primary vLLM host opens an `XPUB` ZeroMQ socket and binds it to ALL interfaces. While the socket is always opened for a multi-node deployment, it is only used when doing tensor parallelism across multiple hosts.

Any client with network access to this host can connect to this `XPUB` socket unless its port is blocked by a firewall. Once connected, these arbitrary clients will receive all of the same data broadcasted to all of the secondary vLLM hosts. This data is internal vLLM state information that is not useful to an attacker.

By potentially connecting to this socket many times and not reading data published to them, an attacker can also cause a denial of service by slowing down or potentially blocking the publisher.

### Detailed Analysis

The `XPUB` socket in question is created here:

https://github.com/vllm-project/vllm/blob/c21b99b91241409c2fdf9f3f8c542e8748b317be/vllm/distributed/device_communicators/shm_broadcast.py#L236-L237

Data is published over this socket via `MessageQueue.enqueue()` which is called by `MessageQueue.broadcast_object()`:

https://github.com/vllm-project/vllm/blob/790b79750b596043036b9fcbee885827fdd2ef3d/vllm/distributed/device_communicators/shm_broadcast.py#L452-L453

https://github.com/vllm-project/vllm/blob/790b79750b596043036b9fcbee885827fdd2ef3d/vllm/distributed/device_communicators/shm_broadcast.py#L475-L478

The `MessageQueue.broadcast_object()` method is called by the `GroupCoordinator.broadcast_object()` method in `parallel_state.py`:

https://github.com/vllm-project/vllm/blob/790b79750b596043036b9fcbee885827fdd2ef3d/vllm/distributed/parallel_state.py#L364-L366

The broadcast over ZeroMQ is only done if the `GroupCoordinator` was created with `use_message_queue_broadcaster` set to `True`:

https://github.com/vllm-project/vllm/blob/790b79750b596043036b9fcbee885827fdd2ef3d/vllm/distributed/parallel_state.py#L216-L219

The only case where `GroupCoordinator` is created with `use_message_queue_broadcaster` is the coordinator for the tensor parallelism group:

https://github.com/vllm-project/vllm/blob/790b79750b596043036b9fcbee885827fdd2ef3d/vllm/distributed/parallel_state.py#L931-L936

To determine what data is broadcasted to the tensor parallism group, we must continue tracing. `GroupCoordinator.broadcast_object()` is called by `GroupCoordinator.broadcoast_tensor_dict()`:

https://github.com/vllm-project/vllm/blob/790b79750b596043036b9fcbee885827fdd2ef3d/vllm/distributed/parallel_state.py#L489

which is called by `broadcast_tensor_dict()` in `communication_op.py`:

https://github.com/vllm-project/vllm/blob/790b79750b596043036b9fcbee885827fdd2ef3d/vllm/distributed/communication_op.py#L29-L34

If we look at `_get_driver_input_and_broadcast()` in the V0 `worker_base.py`, we'll see how this tensor dict is formed:

https://github.com/vllm-project/vllm/blob/790b79750b596043036b9fcbee885827fdd2ef3d/vllm/worker/worker_base.py#L332-L352

but the data actually sent over ZeroMQ is the `metadata_list` portion that is split from this `tensor_dict`. The tensor parts are sent via `torch.distributed` and only metadata about those tensors is sent via ZeroMQ.

https://github.com/vllm-project/vllm/blob/54a66e5fee4a1ea62f1e4c79a078b20668e408c6/vllm/distributed/parallel_state.py#L61-L83

### Patches

* https://github.com/vllm-project/vllm/pull/17197

### Workarounds

Prior to the fix, your options include:
1. Do not expose the vLLM host to a network where any untrusted connections may reach the host.
2. Ensure that only the other vLLM hosts are able to connect to the TCP port used for the `XPUB` socket. Note that port used is random.

### References

* Relevant code first introduced in https://github.com/vllm-project/vllm/pull/6183

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-9f8f-2vmf-885j
- https://nvd.nist.gov/vuln/detail/CVE-2025-30202
- https://github.com/vllm-project/vllm/pull/17197
- https://github.com/vllm-project/vllm/pull/6183
- https://github.com/vllm-project/vllm/commit/a0304dc504c85f421d38ef47c64f83046a13641c
- https://github.com/advisories/GHSA-9f8f-2vmf-885j
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2016.yaml
- https://github.com/vllm-project/vllm
- https://pypi.org/project/vllm
