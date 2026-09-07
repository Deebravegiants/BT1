# [M] RPC service DOS

## Summary
Severity: Medium (CVSS 5.3)
Program: Monero
Weakness: Uncontrolled Resource Consumption
Reporter: ptrstr
State: resolved
Disclosed: 2025-05-23T14:25:17.381Z
Source: https://hackerone.com/reports/2338094

## Details
## Summary:
The RPC service running port 18081 (or 28081, 38081) is vulnerable to a DOS rendering the service unusable. This is due to the possibility of a for loop going up until uint64_t's max range (1<<64 - 1).

On the `get_fee_estimate` JSON RPC endpoint, a `uint64_t` parameter `grace_blocks` can be passed. If this parameter is big and the node is on a `hard_fork` version `15` or above, `get_dynamic_base_fee_estimate_2021_scaling` will be called.
https://github.com/monero-project/monero/blob/v0.18.3.1/src/rpc/core_rpc_server.h#L177
{F3012477}

This handler will then be called:
https://github.com/monero-project/monero/blob/v0.18.3.1/src/rpc/core_rpc_server.cpp#L2956
{F3012488}

This function is then called
https://github.com/monero-project/monero/blob/v0.18.3.1/src/cryptonote_core/blockchain.cpp#L3830
{F3012496}

## Releases Affected:
From my research, all versions after commit [b030f207517f59a5122409398549a02ac23829ae](https://github.com/monero-project/monero/commit/b030f207517f59a5122409398549a02ac23829ae) are vulnerable.
  * v0.18.3.1
  * v0.18.3.0
  * v0.18.2.2
  * v0.18.2.1
  * v0.18.2.0
  * v0.18.1.2
  * v0.18.1.1
  * v0.18.1.0
  * v0.18.0.0 

## Steps To Reproduce:
  1. Start a Monero node with the RPC port opened.
  2. Verify the node is using `hard_fork` version `15` or above
    - To do this, you can do the [`hard_fork_info` JSON RPC request](https://www.getmonero.org/resources/developer-guides/daemon-rpc.html#hard_fork_info)
  3. Perform a few asynchronous requests to the [`get_fee_estimate` JSON RPC endpoint](https://www.getmonero.org/resources/developer-guides/daemon-rpc.html#get_fee_estimate) with `grace_blocks` set to a very very large integer (can go up to 18446744073709551615)
  4. The server should now not be responsive on the RPC port.

## Supporting Material/References:
**Attached is a PoC script using Python's `requests` module to send 500 requests to a server.**
*To run the script, make sure to change the `HOST` variable at the top of the file. You can just replace `127.0.0.1` with any IP you want where a Monero node is running.*


_Trimmed to 38 lines — full report: https://hackerone.com/reports/2338094_
