# [H] CL-2026-02: Memory leak causes P2P crash

## Summary
Severity: High
Chain: Ethereum (consensus layer)
Component: Lodestar
Source: https://notes.ethereum.org/MyfZzN3pQ2OWYFPgCXe81g
Type: ef-disclosure

## Details
Memory leak vulnerability in Lodestar Ethereum beacon node causing remote P2P out of memory crash.  
Attack scenario *
More detailed description of the attack/bug scenario and unexpected/buggy behaviour
The memory leak vulnerability in the Lodestar Ethereum beacon node's P2P network code allows a remote attacker to exploit the node and cause an out of memory crash. The attacker crafts a C++ program that leverages the Boost library to generate a high volume of socket requests targeted at the Lodestar node's P2P network port (9000). By repeatedly sending these requests, the attacker triggers the memory leak within the Lodestar node.  

The affected code in the Lodestar Ethereum beacon node is not properly managing and cleaning up memory when handling incoming requests. As the attacker sends a continuous stream of requests, the memory consumption of the Lodestar node's process starts increasing. This uncontrolled memory growth eventually results in the process consuming all available memory, leading to a crash within 3-4 minutes. This crash fully crashes the Lodestar node and makes it inaccessible with no automatic recovery even if the attack is stopped.

Under normal circumstances, the Lodestar node should be able to handle incoming requests without memory leaks, maintaining stable memory usage regardless of the volume of requests. The vulnerability exposes an unexpected behavior in the node's P2P network code, compromising the stability and security of the affected nodes.

The memory leak occurs in the libp2p P2P network code handling incoming connections and requests.

To debug the memory leak and out of memory crash, our team recorded the memory allocation of the running Lodestar node while simulating the attack.

Heatmap screenshot: https://imgur.com/a/aY1wqn1

We can provide the full heapmap upon request. 

The memory leak is within the libp2p onSocket, and an anonymous function promise to close sockets used within Lodestar.

onSocket: https://github.com/libp2p/js-libp2p-tcp/blob/3f4aa505d3c490b5f8760d1ee474889b70be7227/src/listener.ts#L153  

Anonymous function: https://github.com/libp2p/js-libp2p-tcp/blob/3f4aa505d3c490b5f8760d1ee474889b70be7227/src/listener.ts#L213  
Impact *
 Describe the effect this may have in a production setting
The production impact of this vulnerability is the ability to crash and keep offline all Lodestar nodes on the Ethereum network. While this may have further impacts on the trust of stakers in the security of running lesser popular Beacon clients and the resulting decrease in client diversity, we will only study the direct cost impacts here.
The vulnerability affects 0.74% of the 559,812 Ethereum beacon nodes, or a total of roughly 4,142 beacon nodes. There is currently 17,868,168 ETH staked, which translates to an interpolation of approximately 132,224 ETH staked through Lodestar nodes.

With an estimated APR of 4.7%, a validator earns an APR of approximately 0.0128% daily. The 132,224 ETH staking through Lodestar nodes earn approximately 17 ETH daily.

In the absence of an inactivity leak, validators on the Ethereum network are penalized equivalent to their reward in the case of missed attestations.

Our disclosed vulnerability can quickly bring down all Lodestar nodes on the Ethereum network, leading to stakers being penalized 17 ETH daily, leading to a net loss of 34 ETH daily compared to normal operation.

Assuming it takes 1 week for the Lodestar team to find the issue, patch the vulnerability and for all Lodestar nodes on the network to upgrade after an attack, the total cost to Ethereum stakers through Lodestar nodes could be upwards of 238 ETH (~$430,000 USD)

The cost to execute the attack against 4,142 beacon nodes is less than $1000 as a single machine can remotely crash dozens of Lodestar nodes concurrently, plus crashed nodes do not automatically recover.
Components *
Point to the files, functions, and/or specific line numbers where the bug occurs

_Trimmed to 38 lines — full report: https://notes.ethereum.org/MyfZzN3pQ2OWYFPgCXe81g_
