# [?] Correct a race condition when dialing peers (#4056)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2023-03-16
Source: https://github.com/sigp/lighthouse/commit/3d99ce25f83224da2cea20936fc03ff21635460a
Type: security-commit

## Details
Correct a race condition when dialing peers (#4056)

There is a race condition which occurs when multiple discovery queries return at almost the exact same time and they independently contain a useful peer we would like to connect to.

The condition can occur that we can add the same peer to the dial queue, before we get a chance to process the queue. 
This ends up displaying an error to the user: 
```
ERRO Dialing an already dialing peer
```
Although this error is harmless it's not ideal. 

There are two solutions to resolving this:
1. As we decide to dial the peer, we change the state in the peer-db to dialing (before we add it to the queue) which would prevent other requests from adding to the queue. 
2. We prevent duplicates in the dial queue

This PR has opted for 2. because 1. will complicate the code in that we are changing states in non-intuitive places. Although this technically adds a very slight performance cost, its probably a cleaner solution as we can keep the state-changing logic in one place.
