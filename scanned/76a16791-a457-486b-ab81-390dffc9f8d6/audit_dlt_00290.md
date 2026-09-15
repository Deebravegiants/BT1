# [M] EL-2022-13: Nethermind ModExp Consensus Failure (OutOfMemory Exception)

## Summary
Severity: Medium
Chain: Ethereum (execution layer)
Component: Nethermind
Published: 2023-05-03
Source: https://gist.github.com/pleasew8t/734fb76304bf8375b60cfc9b46cc9351
Type: ef-disclosure

## Details
## Description

An issue was identified within the Nethermind Ethereum client’s execution layer that could be abused to cause a consensus break from other Ethereum clients. The issue was found in Nethermind’s implementation of the `ModExp` precompile (address `0x5`) and introduced in commit [956658e](https://github.com/NethermindEth/nethermind/commit/956658ef2fec18edda55510931489d5cd3ea1bb1), which is expected to be included in the next release.

The first 96 bytes of the payload for the `ModExp` precompile consists of the `base length`, `exponent length`, and the `modulus length`, which are used to indicate how many bytes to read after the first 96 bytes to retrieve the `base`, `exponent` and `modulus` terms. An excerpt of this logic is shown below, taken from the `GetInputLengths()` function at [ModExpPrecompile.cs#L104](https://github.com/NethermindEth/nethermind/blob/220cc8a077c99ce304f08fce7769872259588f87/src/Nethermind/Nethermind.Evm/Precompiles/ModExpPrecompile.cs#L104)

```csharp
int baseLength = (int)new UInt256(extendedInput.Slice(0, 32), true);
UInt256 expLengthUint256 = new(extendedInput.Slice(32, 32), true);
int expLength = expLengthUint256 > int.MaxValue ? 
                        int.MaxValue : (int)expLengthUint256;
int modulusLength = (int)new UInt256(extendedInput.Slice(64, 32), true);
```

Using these values, the precompile implementation will then proceed to creating memory buffers of sizes `baseLength`, `expLength`, and `modulusLength`, and copy the specified amount of data from the input buffer at different offsets. This is shown in the excerpt below, taken from the `Run()` function at [ModExpPrecompile.cs#L118](https://github.com/NethermindEth/nethermind/blob/220cc8a077c99ce304f08fce7769872259588f87/src/Nethermind/Nethermind.Evm/Precompiles/ModExpPrecompile.cs#L118)

```csharp
(int baseLength, int expLength, int modulusLength) = GetInputLengths(inputData);

byte[] modulusData = inputData.Span.SliceWithZeroPaddingEmptyOnError(
         96 + baseLength + expLength, modulusLength);
using mpz_t modulusInt = ImportDataToGmp(modulusData);

byte[] baseData = inputData.Span.SliceWithZeroPaddingEmptyOnError(
         96, baseLength);
using mpz_t baseInt = ImportDataToGmp(baseData);

byte[] expData = inputData.Span.SliceWithZeroPaddingEmptyOnError(
          96 + baseLength, expLength);
using mpz_t expInt = ImportDataToGmp(expData);

if (gmp_lib.mpz_sgn(modulusInt) == 0)
{
   return (new byte[modulusLength], true);
}
```

In the above code, the call to `SliceWithZeroPaddingEmptyOnError()` does the following:

- Check that `inputData` contains more than `zero` bytes at a specific offset, for a specific length. In the case of `expData`, this means the payload needs to have more than 1 byte after offset `96 + baseLength`
- Allocate a buffer of size `length`, which, following the `expData` example, would be `expLength`
- Right-pad the buffer, in the event that the payload does not contain the full `length` as indicated

After reading the input, the implementation will then check if the supplied `modulus` is `zero` and, if so, return in a way that is consistent with other Ethereum execution clients.

However, if it is possible to provide a payload that specifies a large enough `length` for one of the fields, an `OutOfMemory` exception would be thrown, and the Nethermind execution client would return empty data, and indicate that the call failed, to the caller (contract or EOA). This would be at odds with other Ethereum clients, such as Geth (see [contracts.go#L363](https://github.com/ethereum/go-ethereum/blob/fb75f11e87420ec25ff72f7eeeb741fa8974e87e/core/vm/contracts.go#L363)) and Besu (see [BigIntegerModularExponentiationPrecompiledContract.java#L57](https://github.com/hyperledger/besu/blob/e9f979ebd3ab338682c603bfa31e162c741eee43/evm/src/main/java/org/hyperledger/besu/evm/precompile/BigIntegerModularExponentiationPrecompiledContract.java#L57)), which only allocate memory after the `modulus` check.

This distinction is important, as the gas costs for causing an `OutOfMemory` exception in the `ModExp` precompile implementation of Nethermind is `200`. To show this, consider the gas calculation formula for `ModExp`, and assume a `length` of `0xffffffff` to be sufficient to cause an `OutOfMemory` exception. *Note that the complexity calculation is not exact, but does illustrate the basic concept.*

```csharp
complexity = ( max(baseLength, modulusLength) / 8)^2
iterations = max(f(explength), 1)

gas = max( complexity * iterations, 200 )
```

- Assume `baseLength = 0xffffffff, modulusLength = 0, expLength = 0`, which would result in `gas = 288230376151711744`, which would be too high gas, and exploitation is prevented
- Assume `baseLength = 0, modulusLength = 0xffffffff, expLength = 0`, which would result in `gas = 288230376151711744`, which would be too high gas, and exploitation is prevented
- Assume `baseLength = 0, modulusLength = 0, expLength = 0xffffffff`, which results in `complexity = 0`, and as a result `complexity * iterations = 0`, and therefore the `gas` is only `200`.

As a result, specifying a large enough `expLength` to cause an `OutOfMemory` exception can be performed cheaply, and the outcome between Nethermind and other clients would be different.

- Clients, such as Geth and Besu, would experience an early-exit for `baseLength = 0` and `modulusLength = 0`, returning empty data and reporting a successful call.
- Nethermind, however, would first attempt to create a buffer of a large number of bytes, causing an `OutOfMemory` exception. These exceptions from precompiles are handled by Nethermind (see [VirtualMachine.cs#L587](https://github.com/NethermindEth/nethermind/blob/220cc8a077c99ce304f08fce7769872259588f87/src/Nethermind/Nethermind.Evm/VirtualMachine.cs#L587)), and will by default return empty data, and report an unsuccessful call.

An example payload that exploits this issue is shown below. It is also used in the attached proof-of-concept.

```
payload: 0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000f0000000000000000000000000000000000000000000000000000000000000000000000000000000000

baseLength = 0
expLength = 0xf00000000 (this is > int.MaxValue, and therefore gets capped to int.MaxValue)
modulusLength = 0

extra bytes: 00 (this is necessary to ensure there are bytes available when allocating memory for expData 
```

### Impact and Risk Rating

As illustrated by the proof of concept, it is possible to break consensus between Nethermind and other execution clients. The exploit is reliable, has no timing considerations, and requires a single, low-cost transaction to be submitted by any user of the network. 
The full impact of such a failure in consensus would be difficult to predetermine. The most obvious concerns would be:

*  Any node using Nethermind would be unable to successfully produce blocks or publish attestations, resulting in the respective stakers likely being penalized. Any blocks produced by an affected node will be rejected by the majority of stakers and could result in skipped slots, reducing the overall throughput of the network.
* Reputational damage to Nethermind, as well as associated entities reliant on the technology, including Ethereum and Gnosis Chain.

Given the ease of exploitation and the associated high degree of impact, a rating of **CRITICAL** would seem appropriate. 

### Remediation

In order to remediate this issue, it is recommended that the memory allocation for `baseData` and `expData` be moved down to after the `if (gmp_lib.mpz_sgn(modulusInt) == 0)` check. Ideally, the precompile’s implementation should follow a similar order of operations as that of Geth and Besu, implying that a check such as `baseLength == 0` be performed. 

### Proof of Concept

[proof-of-concept.zip](https://drive.google.com/file/d/1LgkI79ot6amRI2toRGLW0vRe6E7ZOWJP/view?usp=sharing)

The proof of concept sets up a network containing three Ethereum clients: Nethermind, Geth, and Besu. The steps to start the nodes are as follows:

- Ensure that the latest version of `docker` is installed (https://www.docker.com/)
- Extract the attached zip file `proof-of-concept.zip`
- Run `docker compose down && docker compose rm && docker compose up` from the extracted zip directory to start the nodes

If `foundry`'s utilities are available, the issue can be exploited by executing `cast send --from 0x7ceB437CeDC050C1AE96923DF0D4c2F3b0Bc99f2 0x0000000000000000000000000000000000000005 0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000f0000000000000000000000000000000000000000000000000000000000000000000000000000000000`.

If `foundry` is not available, a hardhat project is supplied under the `hh-project` directory. This will deploy a contract that calls the precompile with the malicious input, and can be run using the following commands:

- `cd hh-project`
- `npm i`
- `npx hardhat run --network localhost scripts/poc.js`

By running the proof of concept, similar output to the following can be observed from the Nethermind client, indicating that the block was deemed invalid, deleted, and the Nethermind client ceases to process any further transactions (`waiting for peers`):

```
Processed block is not valid 3 (0x59b28b22108fd6595efbbdf71dffe1a8ff57857bb5f17f524581fd7fc3d1e9a4) 
Suggested block TD: 7, Suggested block IsPostMerge False, Block TD: 7, Block IsPostMerge False 
Deleting invalid block 0x59b28b22108fd6595efbbdf71dffe1a8ff57857bb5f17f524581fd7fc3d1e9a4 at level 3 
Waiting for peers... 5s 
Waiting for peers... 6s
```

*Note that the above output is abridged for brevity.*
