# [M] EL-2022-11: Slow transaction verification on Besu client

## Summary
Severity: Medium
Chain: Ethereum (execution layer)
Component: Besu
Published: 2023-05-03
Source: https://notes.ethereum.org/zSE44ueJS9-_G7lOzPalEQ
Type: ef-disclosure

## Details
# Slow Transaction Verification on Besu Client
Executive Summary
The Besu execution-layer client (version 22.7.2) has slow verification times for certain transactions. Verification times of more than 24 seconds on Intel Core i7 are possible. Such verification times, allow for different attacks against validators using Besu as execution-layer clients.

Background
Besu is one of the four execution-layer clients officially endorsed by the foundation and version 22.7.2 is the recommended version (https://blog.ethereum.org/2022/08/24/mainnet-merge-announcement). The Ethereum foundation is actively encouraging client diversity, making Besu a relevant attack target.

With the switch to Proof-Of-Stake, transaction verification times become more important as validators have to produce blocks in a 12-second interval. A failure to produce a block within the assigned 12-second interval results in a punishment.

Furthermore, it is important to note that clients announce which software they are using and that the order of block producers is predetermined. This combination in addition to the recent research on linking public keys and IP addresses (https://medium.com/hoprnet/proof-of-stake-validator-sniping-research-8670c4a88a1c) and the likely co-location of consensus-layer and execution-layer nodes, makes us believe that it will be possible to predict which blocks will be produced using Besu clients.

Attack Strategy
The EVM memory can be imagined like a byte array that is being expanded on demand by blocks of 32 bytes. Our findings suggest that Besu is slow in validating transactions that require a lot of such memory expansions. In Besu’s code this appears as:

  if (endIndex > srcSize) {
    final MutableBytes paddedAnswer = MutableBytes.create((int) length);
    if (sourceOffset < srcSize) {
      value.slice((int) sourceOffset, (int) (srcSize - sourceOffset)).copyTo(paddedAnswer, 0);
    }
    setUpdatedMemory(offset, paddedAnswer.copy());
  } else {
    setUpdatedMemory(offset, value.slice((int) sourceOffset, (int) length).copy());
  }
(https://github.com/hyperledger/besu/blob/22.7.2/evm/src/main/java/org/hyperledger/besu/evm/frame/MessageFrame.java#L690-L698)

Hence, we constructed an attack transaction that performs the following steps in a loop:

   PC      // This is just a cheap way to push a value onto the stack
   MSIZE   // This is the memory offset we want to write to
   MSTORE  // This performs the memory storage and thereby the memory expansion   
In every loop iteration we thereby force a memory expansion which is a relatively slow operation in Besu. We use an infinite loop and simply run it until we run out-of-gas. The fact that the transaction reverts does not impact the attack, as the whole point is to occupy the validator for as long as possible.

Please note that this attack is not fully optimized. Likely higher verification times are possible. We are reporting as quickly as possible and will investigate further.

Measurements
We performed the measurements with the following state test and the Besu EVM, version 22.7.2. The state test calls the previously described contract with a gas limit of 30 million gas, which matches the current limit. We used the following command to perform the state test on Besu:

time ./evm state-test state-test-mstoreloop.json

_Trimmed to 38 lines — full report: https://notes.ethereum.org/zSE44ueJS9-_G7lOzPalEQ_
