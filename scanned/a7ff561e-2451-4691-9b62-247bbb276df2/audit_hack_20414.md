# [H] OtterSec: Cosmos security: an otter’s guide

## Summary
Severity: High
Published: Tue, 10 Jun 2025
Source: https://osec.io/blog/cosmos-security/
Type: security-research

## Details
## Cosmos security: an otterâs guide

 James Wang Jun 10, 2025 #cosmos-sdk #security From infinite loops and map determinism to AnteHandler missteps and storage key collisions, we highlight real-world vulnerabilities and actionable advice for building safer Cosmos-based projects.

## Introduction 

 The Cosmos SDK is an âL1 toolkitâ for developers. It provides an open-source tool that enhances the ability to build application-specific L1 chains, all while prioritizing flexibility and control over the entire runtime environment. Unfortunately, with the convenience of the Cosmos SDK, security can be an oversight.

 In this comprehensive blog post, we break down security issues that are often overlooked by developers, supported by real-world examples from live projects. Our goal is to provide a practical exploration of security vulnerabilities while also offering insights on how developers can identify and address these issues on their own.

## Itâs loopinâ time 

 There are notable differences between building app-specific L1s using the SDK and building contracts on established L1 chains. It is especially crucial to recognize that maintaining the stability of a blockchain is dependent on the developer.

 Below, we begin to demonstrate the differences between writing smart contracts with Solidity vs. developing an L1 with the Cosmos SDK.

 Here is a simple example for reference:

```

```
 1

 function sumWithStride ( 

 2

 uint64 start , 

 3

 uint64 stride , 

 4

 uint64 [] memory arr 

 5

 ) public returns ( uint64 ) { 

 6

 uint64 idx = start ; 

 7

 uint64 sum = 0 ; 

 8

 uint64 end = arr . length ; 

 9

 10

 while ( idx < end ) { 

 11

 sum += arr [ idx ]; 

 12

 idx += stride ; 

 13

 } 

 14

 return sum ; 

 15

 } 

```

```

```

```
 1

 type MsgSumWithStrideParams struct { 

 2

 Start uint64 

 3

 Stride uint64 

 4

 Arr [] uint64 

 5

 } 

 6

 7

 type MsgSumWithStrideResponse struct { 

 8

 Sum uint64 

 9

 } 

 10

 11

 func ( ms msgServer ) SumWithStride ( 

 12

 goCtx context . Context , 

 13

 msg * MsgSumWithStrideParams , 

 14

 ) (* MsgSumWithStrideResponse , error ) { 

 15

 sum := uint64 ( 0 ) 

 16

 end := uint64 ( len ( msg . Arr )) 

 17

 for idx := msg . Start ; idx < end ; idx += msg . Stride { 

 18

 sum += msg . Arr [ idx ] 

 19

 } 

 20

 return & MsgSumWithStrideResponse { Sum : sum }, nil 

 21

 } 

```

```

 The provided Solidity/Cosmos snippets feature a public function that calculates the sum of an array using a provided starting 
```
idx
```
 and a 
```
stride
```
. It is crucial to note that this function lacks robustness. A keen observer might have already identified that if the user supplies a stride value of 0, the code will result in an infinite loop.

 While an infinite loop is not ideal for Solidity, it may still be tolerable. The underlying blockchain on which a smart contract operates is responsible for monitoring the gas and computation budget. It will intervene and terminate the execution at a certain point. Interestingly, those types of âunhandled errorâ patterns are quite common occurrences in contracts.

 However, the same logic does not directly apply to Cosmos. In Cosmos, users are responsible for implementing the entire L1, and there is no underlying computation budget tracker that automatically stops code execution. As a result, any potential logic DoS or infinite loop can directly lead to the custom Cosmos L1 chain halting or stalling.

 This toy scenario captures the importance of attention to error handling, edge cases, and overall robustness in Cosmos.

## Real-world examples 

 Now, letâs examine a few real-world instances.

 In the case of this CosmWasm bug , the helper method 
```
 write_to_contract 
```
 negligently calls the untrusted Wasm function 
```
 "allocate" 
```
 ( permalink ):

 imports.rs 
```

```
 1

 fn write_to_contract < A : BackendApi , S : Storage , Q : Querier >( 

 2

 env : & Environment < A , S , Q >, 

 3

 input : &[ u8 ], 

 4

 ) -> VmResult < u32 > { 

 5

 let out_size = to_u32 ( input . len ())?; 

 6

 let result = env . call_function1 ( "allocate" , &[ out_size . into ()])?; 

 7

 let target_ptr = ref_to_u32 (& result )?; 

 8

 if target_ptr == 0 { 

 9

 return Err ( CommunicationError :: zero_address (). into ()); 

 10

 } 

 11

 write_region (& env . memory (), target_ptr , input )?; 

 12

 Ok ( target_ptr ) 

 13

 } 

```

```

 ( env: &Environment , input: &[u8],) -> VmResult { let out_size = to_u32(input.len())?; let result = env.call_function1("allocate", &[out_size.into()])?; let target_ptr = ref_to_u32(&result)?; if target_ptr == 0 { return Err(CommunicationError::zero_address().into()); } write_region(&env.memory(), target_ptr, input)?; Ok(target_ptr)}"> 

 As users have complete control over 
```
allocate
```
, there is a possibility to call back 
```
 write_to_contract 
```
 repeatedly through other imported functions. This can result in the depletion of the host stack and ultimately lead to a DoS.

 Additional real-world examples include not returning proper values for malformed txs .

## Order was the dream of man 

 Unlike Solidity, which is a domain-specific language for smart contracts, Golang is general-purpose. Therefore, developers must be mindful of specific footguns. One notable instance is non-determinism.

 Consider a scenario where there is a requirement to emit an event for every entry in a map. It might be tempting to implement this as demonstrated below:

```

```
 1

 type ObjectMap map [ string ] string 

 2

 3

 func EmitEntries ( objectMap ObjectMap ) { 

 4

 for key , value := range objectMap { 

 5

 ctx . EventManager . EmitEvent ( 

 6

 sdk . NewEvent ( 

 7

 "MapContext" , 

 8

 sdk . NewAttribute ( key , value ), 

 9

 ) 

 10

 ) 

 11

 } 

 12

 } 

```

```

 Itâs important to note that Golang map iterators are unordered by design. As stated in the Golang documentation:

 When iterating over a map with a range loop, the iteration order is not specified and is not guaranteed to be the same from one iteration to the next.

 Running the same code with different validators may therefore result in varying event orders, potentially causing consensus problems.

 To correctly implement iteration orders, developers must explicitly sort the keys of the 
```
 map 
```
 and then fetch the values using the sorted key array before emitting them:

```

```
 1

 type ObjectMap map [ string ] string 

 2

 3

 func EmitEntries ( objectMap ObjectMap ) { 

 4

 var keys [] string 

 5

 for key := range objectMap { 

 6

 keys = append ( keys , key ) 

 7

 } 

 8

 sort . Strings ( keys ) 

 9

 10

 for _ , key := range keys { 

 11

 ctx . EventManager . EmitEvent ( 

 12

 sdk . NewEvent ( 

 13

 "MapContext" , 

 14

 sdk . NewAttribute ( key , objectMap [ key ]), 

 15

 ) 

 16

 ) 

 17

 } 

 18

 } 

```

```

 Hidden code within external Golang dependencies makes it difficult to fully avoid these language quirks. It is crucial to remain vigilant and avoid underestimating the gravity of this lingering bug class.

## Real-world examples 

 Real-world examples of 
```
 map 
```
 causing determinism problems can be found here , specifically where the result of 
```
 buildCommitInfo 
```
 is inconsistent due to iteration over the 
```
 rs . stores 
```
 map ( permalink ):

 store.go 
```

```
 1

 func ( rs * Store ) buildCommitInfo ( 

 2

 version int64 

 3

 ) * types . CommitInfo { 

 4

 storeInfos := [] types . StoreInfo {} 

 5

 for key , store := range rs . stores { 

 6

 if store . GetStoreType () == types . StoreTypeTransient { 

 7

 continue 

 8

 } 

 9

 storeInfos = append ( storeInfos , types . StoreInfo { 

 10

 Name : key . Name (), 

 11

 CommitId : store . LastCommitID (), 

 12

 }) 

 13

 } 

 14

 return & types . CommitInfo { 

 15

 Version : version , 

 16

 StoreInfos : storeInfos , 

 17

 } 

 18

 } 

```

```

 Other factors contributing to determinism issues are the usage of time-sensitive functions and race conditions .

## Thou shalt not passâ¦ or should you? 

 When developing smart contracts, it is common to delegate certain low-level tasks (such as parsing 
```
 msg . value 
```
, 
```
 msg.sender 
```
, and collecting transaction fees) to the underlying blockchain.

 On Cosmos, there is no blockchain to rely on since it is the L1 itself! To simplify the development of middleware-like functionalities, the Cosmos SDK introduces 
```
 AnteHandler 
```
 decorators to help accomplish this. While there are pre-written decorators, all other data extraction from transactions and blockchain states must be carried out by the developers themselves.

 To provide context, letâs first understand how an 
```
 AnteHandler 
```
 is processed. Each 
```
 AnteHandler 
```
 is a state transition function that can:

- Transform the block state in relation to transaction and execution context.

- Determine the course of action for the transaction.
 
- Pass the transaction to the next 
```
 AnteHandler 
```
.

- Return an error for the transaction.

 The bad news is that developing an 
```
 AnteHandler 
```
 is not the easiest task. For instance, letâs consider a scenario where we need to ensure all signers involved in a transaction have a balance greater than X at the time of transaction execution.

 The 
```
 AnteHandle 
```
 implementation may look something like this:

```

```
 1

 const ( 

 2

 MIN_BALANCE = 100 

 3

 ) 

 4

 5

 func ( abd AccountBalanceDecorator ) AnteHandle ( 

 6

 ctx sdk . Context , 

 7

 tx sdk . Tx , 

 8

 simulate bool , 

 9

 next sdk . AnteHandler , 

 10

 ) ( sdk . Context , error ) { 

 11

 sigTx , ok := tx .( authsigning . SigVerifiableTx ) 

 12

 if ! ok { 

 13

 return ctx , errorsmod . Wrap ( 

 14

 sdkerrors . ErrTxDecode , 

 15

 "invalid tx type" , 

 16

 ) 

 17

 } 

 18

 19

 signers := sigTx . GetSigners () 

 20

 for i , signer := range signers { 

 21

 balance := abd . bk . getBalance ( ctx , signer , ATOM ) 

 22

 if balance . Amount < MIN_BALANCE { 

 23

 return ctx , errorsmod . Wrap ( 

 24

 ErrInsufficientBalance , 

 25

 "Insufficient Balance" , 

 26

 ) 

 27

 } 

 28

 } 

 29

 30

 return next ( ctx , tx , simulate ) 

 31

 } 

```

```

 Where should this custom 
```
 AnteHandler 
```
 be placed relative to the other 
```
AnteHandlers
```
 provided by the Cosmos SDK? Considering that we are only concerned with transactions that satisfy our check, inserting it right after the 
```
 SetUpContextDecorator 
```
 should work, right? Hereâs the default decorator chain ( permalink ):

 ante.go 
```

```
 1

 anteDecorators := [] sdk . AnteDecorator { 

 2

 NewSetUpContextDecorator (), // outermost AnteDecorator. SetUpContext must be called first 

 3

 // INSERT HERE 

 4

 NewExtensionOptionsDecorator ( options . ExtensionOptionChecker ), 

 5

 NewValidateBasicDecorator (), 

 6

 NewTxTimeoutHeightDecorator (), 

 7

 NewValidateMemoDecorator ( options . AccountKeeper ), 

 8

 NewConsumeGasForTxSizeDecorator ( options . AccountKeeper ), 

 9

 NewDeductFeeDecorator ( options . AccountKeeper , options . BankKeeper , options . FeegrantKeeper , options . TxFeeChecker ), 

 10

 NewSetPubKeyDecorator ( options . AccountKeeper ), // SetPubKeyDecorator must be called before all signature verification decorators 

 11

 NewValidateSigCountDecorator ( options . AccountKeeper ), 

 12

 NewSigGasConsumeDecorator ( options . AccountKeeper , options . SigGasConsumer ), 

 13

 NewSigVerificationDecorator ( options . AccountKeeper , options . SignModeHandler ), 

 14

 NewIncrementSequenceDecorator ( options . AccountKeeper ), 

 15

 } 

```

```

 Unfortunately, that order wouldnât work. This is because there are other 
```
AnteHandlers
```
, such as 
```
 SigGasConsumeDecorator 
```
 and 
```
 ConsumeGasForTxSizeDecorator 
```
, that modify account balances. By placing our decorator at the very start of the chain, we might pass the check and later have the signersâ balances deducted before reaching the end of the decorator chain and starting transaction execution. Consequently, the invariant we intended to ensure may no longer hold, rendering our check useless.

 The easiest âmitigationâ is to move our decorator down the chain list.

 Caution We say this lightly because itâs important to consider various factors, such as whether nested 
```
msgs
```
 are allowed (e.g. the authz module is present), as this precaution alone might not be enough to fully resolve the issue. Without a comprehensive understanding of the entire system, there is a risk that mistakes will still be made in the 
```
 AnteHandle 
```
 chain.

## Real-world examples 

 An instance of 
```
 AnteHandler 
```
 misuse is a theft of funds bug that was exploited in a Cronos contract.

 In this scenario, 
```
msgs
```
 are multiplexed to different 
```
 AnteHandler 
```
 sets through the user-controlled 
```
 ExtensionOptionsEthereumTx 
```
 option. However, due to a lack of tx validation, if a 
```
 MsgEthereumTx 
```
 does not have 
```
 ExtensionOptionsEthereumTx 
```
 specified, it will be routed to non-Ethereum 
```
AnteHandlers
```
, failing to collect fees from users as intended. Consequently, attackers can exploit the fee refund at the end of transaction processing to steal funds ( permalink ):

 ante.go 
```

```
 1

 func NewAnteHandler ( 

 2

 ak evmtypes . AccountKeeper , 

 3

 bankKeeper evmtypes . BankKeeper , 

 4

 evmKeeper EVMKeeper , 

 5

 feeGrantKeeper authante . FeegrantKeeper , 

 6

 channelKeeper channelkeeper . Keeper , 

 7

 signModeHandler authsigning . SignModeHandler , 

 8

 ) sdk . AnteHandler { 

 9

 return func ( 

 10

 ctx sdk . Context , tx sdk . Tx , sim bool , 

 11

 ) ( newCtx sdk . Context , err error ) { 

 12

 var anteHandler sdk . AnteHandler 

 13

 14

 defer Recover ( ctx . Logger (), & err ) 

 15

 16

 txWithExtensions , ok := tx .( authante . HasExtensionOptionsTx ) 

 17

 if ok { 

 18

 opts := txWithExtensions . GetExtensionOptions () 

 19

 if len ( opts ) > 0 { 

 20

 switch typeURL := opts [ 0 ]. GetTypeUrl (); typeURL { 

 21

 case "/ethermint.evm.v1.ExtensionOptionsEthereumTx" : 

 22

 // handle as *evmtypes.MsgEthereumTx 

 23

 24

 anteHandler = sdk . ChainAnteDecorators ( 

 25

 NewEthSetUpContextDecorator (), // outermost AnteDecorator. SetUpContext must be called first 

 26

 ... 

 27

 NewEthIncrementSenderSequenceDecorator ( ak ), // innermost AnteDecorator. 

 28

 ) 

 29

 30

 default : 

 31

 return ctx , stacktrace . Propagate ( 

 32

 sdkerrors . Wrap ( sdkerrors . ErrUnknownExtensionOptions , typeURL ), 

 33

 "rejecting tx with unsupported extension option" , 

 34

 ) 

 35

 } 

 36

 37

 return anteHandler ( ctx , tx , sim ) 

 38

 } 

 39

 } 

 40

 41

 // SHOULD CHECK TX IS NOT MsgEthereumTx HERE 

 42

 43

 switch tx .( type ) { 

 44

 case sdk . Tx : 

 45

 anteHandler = sdk . ChainAnteDecorators ( 

 46

 authante . NewSetUpContextDecorator (), // outermost AnteDecorator. SetUpContext must be called first 

 47

 ... 

 48

 authante . NewIncrementSequenceDecorator ( ak ), // innermost AnteDecorator 

 49

 ) 

 50

 default : 

 51

 return ctx , stacktrace . Propagate ( 

 52

 sdkerrors . Wrapf ( sdkerrors . ErrUnknownRequest , "invalid transaction type: %T " , tx ), 

 53

 "transaction is not an SDK tx" , 

 54

 ) 

 55

 } 

 56

 57

 return anteHandler ( ctx , tx , sim ) 

 58

 } 

 59

 } 

```

```

 0 { switch typeURL := opts[0].GetTypeUrl(); typeURL { case "/ethermint.evm.v1.ExtensionOptionsEthereumTx": // handle as *evmtypes.MsgEthereumTx anteHandler = sdk.ChainAnteDecorators( NewEthSetUpContextDecorator(), // outermost AnteDecorator. SetUpContext must be called first ... NewEthIncrementSenderSequenceDecorator(ak), // innermost AnteDecorator. ) default: return ctx, stacktrace.Propagate( sdkerrors.Wrap(sdkerrors.ErrUnknownExtensionOptions, typeURL), "rejecting tx with unsupported extension option", ) } return anteHandler(ctx, tx, sim) } } // SHOULD CHECK TX IS NOT MsgEthereumTx HERE switch tx.(type) { case sdk.Tx: anteHandler = sdk.ChainAnteDecorators( authante.NewSetUpContextDecorator(), // outermost AnteDecorator. SetUpContext must be called first ... authante.NewIncrementSequenceDecorator(ak), // innermost AnteDecorator ) default: return ctx, stacktrace.Propagate( sdkerrors.Wrapf(sdkerrors.ErrUnknownRequest, "invalid transaction type: %T", tx), "transaction is not an SDK tx", ) } return anteHandler(ctx, tx, sim) }}"> 

 Additional examples of incorrect 
```
 AnteHandler 
```
 usage include yet more bypassable checks and loss of funds and incorrect data passing between blockchains .

## Errors? Panics? I can handle it 

 Smart contract developers are used to not properly handling errors. This is acceptable since most underlying blockchains revert all state changes when execution fails.

 Cosmos is designed to provide a similar experience. Whenever some message handler returns an error, changes to the persistent state are dropped. Panics are handled similarly, where a recovery handler is wrapped around the message execution to convert panics into errors for a downstream process.

 This design is pretty neat and allows developers to write code in a rather lazy way. For instance, the following code works perfectly fine â if 
```
 k . keeper . TotalReward () 
```
 returns zero, the 
```
msg
```
 execution will simply roll back as if nothing has happened:

```

```
 1

 func ( k msgServer ) AllocateReward ( 

 2

 goCtx context . Context , 

 3

 msg * types . MsgAllocateReward ) 

 4

 (* types . MsgAllocatRewardResponse , error ) { 

 5

 6

 RewardPerShare := k . keeper . Shares () / k . keeper . TotalReward () 

 7

 k . keeper . DistributeReward ( RewardPerShare ) 

 8

 9

 return & types . MsgAllocateRewardResponse , nil 

 10

 } 

```

```

 However, the same assumption does not always hold. Certain parts of Cosmos, such as 
```
 PreBlocker 
```
, 
```
 BeginBlocker 
```
, and 
```
 EndBlocker 
```
, are not protected by the error handling mechanism. So, if we move the reward distribution logic into 
```
 BeginBlocker 
```
 to automatically distribute rewards at the start of each block, panics raised by division by 0 will halt the chain:

```

```
 1

 func BeginBlocker ( ctx context . Context , keeper keeper . Keeper ) error { 

 2

 3

 RewardPerShare := keeper . Shares () / keeper . TotalReward () 

 4

 keeper . DistributeReward ( RewardPerShare ) 

 5

 6

 return nil 

 7

 } 

```

```

## Real-world examples 

 Recently, developers have become increasingly aware of unprotected ABCI functions, but this doesnât stop DoS bugs from manifesting. So what is the catch?

 The problem lies in the lack of proper understanding of utility functions. The example here implements a bridge that mints wrapped BTC tokens in the 
```
 PreBlocker 
```
 when bridging events are observed. Notably, errors returned by 
```
 bankKeeper . SendCoinsFromModuleToAccount 
```
 will be bubbled up through 
```
 PreBlocker 
```
 and halt the chain. It turns out an attacker can force 
```
 SendCoinsFromModuleToAccount 
```
 to return an error by setting 
```
recipient
```
 to some 
```
 BlockedAddr 
```
, rendering the code susceptible to DoS attacks ( permalink ):

 assets_locked.go 
```

```
 1

 func ( pbh * PreBlockHandler ) PreBlocker () sdk . PreBlocker { 

 2

 return func ( 

 3

 ctx sdk . Context , 

 4

 req * cmtabci . RequestFinalizeBlock , 

 5

 ) (* sdk . ResponsePreBlock , error ) { 

 6

 ... 

 7

 err := pbh . bridgeKeeper . AcceptAssetsLocked ( ctx , events ) 

 8

 if err != nil { 

 9

 return nil , fmt . Errorf ( "cannot accept AssetsLocked events: %w " , err ) 

 10

 } 

 11

 ... 

 12

 } 

 13

 } 

 14

 15

 func ( k Keeper ) AcceptAssetsLocked ( 

 16

 ctx sdk . Context , 

 17

 events types . AssetsLockedEvents , 

 18

 ) error { 

 19

 ... 

 20

 for _ , event := range events { 

 21

 recipient , err := sdk . AccAddressFromBech32 ( event . Recipient ) 

 22

 if err != nil { 

 23

 return fmt . Errorf ( "failed to parse recipient address: %w " , err ) 

 24

 } 

 25

 26

 if bytes . Equal ( event . TokenBytes (), sourceBTCToken ) { 

 27

 err = k . mintBTC ( ctx , recipient , event . Amount ) 

 28

 if err != nil { 

 29

 return fmt . Errorf ( 

 30

 "failed to mint BTC for event %v : %w " , 

 31

 event . Sequence , 

 32

 err , 

 33

 ) 

 34

 } 

 35

 } else { 

 36

 ... 

 37

 } 

 38

 } 

 39

 ... 

 40

 } 

 41

 42

 func ( k Keeper ) mintBTC ( 

 43

 ctx sdk . Context , 

 44

 recipient sdk . AccAddress , 

 45

 amount math . Int , 

 46

 ) error { 

 47

 ... 

 48

 err = k . bankKeeper . SendCoinsFromModuleToAccount ( 

 49

 ctx , 

 50

 types . ModuleName , 

 51

 recipient , 

 52

 coins , 

 53

 ) 

 54

 if err != nil { 

 55

 return fmt . Errorf ( "failed to send coins: %w " , err ) 

 56

 } 

 57

 ... 

 58

 } 

```

```

 keeper.go 
```

```
 1

 func ( k BaseKeeper ) SendCoinsFromModuleToAccount ( 

 2

 ctx context . Context , senderModule string , recipientAddr sdk . AccAddress , amt sdk . Coins , 

 3

 ) error { 

 4

 ... 

 5

 if k . BlockedAddr ( recipientAddr ) { 

 6

 return errorsmod . Wrapf ( sdkerrors . ErrUnauthorized , " %s is not allowed to receive funds" , recipientAddr ) 

 7

 } 

 8

 ... 

 9

 } 

```

```

 This shows even well-known bug classes still resurface from time to time due to unforeseen invariant violations. Additional examples include improper decimal handling in the group module .

## Same, sameâ¦ but different 

 Cosmos exposes several consensus-level interfaces, such as 
```
 PrepareProposal 
```
, 
```
 ProcessProposal 
```
, 
```
 ExtendVote 
```
, and 
```
 VerifyVoteExtension 
```
. These ABCI methods allow developers to customize how blocks are constructed, as well as inject supplementary data into each block.

 Two of the best-known attack surfaces are:

- 
```
 PrepareProposal 
```
 (
```
 ExtendVote 
```
) outputs being rejected due to 
```
 ProcessProposal 
```
 (
```
 VerifyVoteExtension 
```
) over-validating, resulting in liveness failures.

- Malicious proposals and vote extensions not created through 
```
 PrepareProposal 
```
 (
```
 ExtendVote 
```
) being accepted due to 
```
 ProcessProposal 
```
 (
```
 VerifyVoteExtension 
```
) under-validating.

 In essence, any difference in pairs of handlers will likely lead to security issues.

 There are also a few lesser-known variants of these issues. One instance is the validation of 
```
VoteExtensions
```
 within 
```
 PrepareProposal 
```
. To provide context, we start with a primer on the CometBFT consensus and vote extensions:

 Note (How CometBFT consensus works) Consensus starts with a leader creating a proposal and then broadcasting it to each validator. Validators then proceed to vote on whether or not to accept the proposal. During the voting phase, 
```
 ExtendVote 
```
 is called to attach additional data to the votes. Once a validator collects enough valid votes that pass 
```
 VerifyVoteExtension 
```
, a proposal is considered accepted and can be committed. After committing the proposal, a new leader starts to create the next proposal, bringing us back to the point where we started.

 So, where is the attached vote extension data used? It turns out a leader should include the vote extensions of the previous consensus round in its proposal. It might be tempting to conclude that all vote extensions an honest leader accepted have passed the 
```
 VerifyVoteExtension 
```
 check and are therefore valid. Thus, we can directly inject all vote extensions into our proposal.

 Unfortunately, CometBFT directly accepts late precommits without passing them through 
```
 VerifyVoteExtension 
```
. This exposes a time window where Byzantine validators can smuggle malicious votes into the next leaderâs cache, luring the leader into including invalid vote extensions in its 
```
Proposal
```
:

 state.go 
```

```
 1

 func ( cs * State ) addVote ( vote * types . Vote , peerID p2p . ID ) ( added bool , err error ) { 

 2

 ... 

 3

 4

 // A precommit for the previous height? 

 5

 // These come in while we wait timeoutCommit 

 6

 if vote . Height + 1 == cs . Height && vote . Type == types . PrecommitType { 

 7

 ... 

 8

 // Late precommits are not checked by VerifyVoteExtension 

 9

 added , err = cs . LastCommit . AddVote ( vote ) 

 10

 ... 

 11

 return added , err 

 12

 } 

 13

 extEnabled := cs . state . ConsensusParams . Feature . VoteExtensionsEnabled ( vote . Height ) 

 14

 if extEnabled { 

 15

 ... 

 16

 if vote . Type == types . PrecommitType && ! vote . BlockID . IsNil () && 

 17

 ! bytes . Equal ( vote . ValidatorAddress , myAddr ) { // Skip the VerifyVoteExtension call if the vote was issued by this validator. 

 18

 ... 

 19

 err := cs . blockExec . VerifyVoteExtension ( context . TODO (), vote ) 

 20

 ... 

 21

 } 

 22

 } else if { 

 23

 ... 

 24

 } 

 25

 ... 

 26

 } 

```

```

 If developers are not aware of the subtle details regarding vote extension handling in CometBFT, it is quite easy to overlook implementing protections against these attacks.

## Real-world examples 

 An example of the bug we just described is shown below. 
```
 PrepareProposal 
```
 only checks that each vote is properly signed by a validator in 
```
 ValidateVoteExtensions 
```
 but does not verify it against the rules in 
```
 VerifyVoteExtension 
```
, therefore leaving the leader vulnerable to accepting malicious vote extensions in their proposals ( permalink ):

 handlers.go 
```

```
 1

 func ( h * Handlers ) PrepareProposalHandler () sdk . PrepareProposalHandler { 

 2

 return func ( ctx sdk . Context , req * abcitypes . RequestPrepareProposal ) (* abcitypes . ResponsePrepareProposal , error ) { 

 3

 ... 

 4

 var injection [] byte 

 5

 if req . Height > ctx . ConsensusParams (). Abci . VoteExtensionsEnableHeight && collectSigs { 

 6

 //Fails to verify vote extensions with VerifyVoteExtension rules 

 7

 err := baseapp . ValidateVoteExtensions ( ctx , h . stakingKeeper , req . Height , ctx . ChainID (), req . LocalLastCommit ) 

 8

 if err != nil { 

 9

 return nil , err 

 10

 } 

 11

 injection , err = json . Marshal ( req . LocalLastCommit ) 

 12

 if err != nil { 

 13

 h . logger . Error ( "failed to marshal extended votes" , "err" , err ) 

 14

 return nil , err 

 15

 } 

 16

 ... 

 17

 } 

 18

 defaultRes , err := h . defaultPrepareProposal ( ctx , req ) 

 19

 ... 

 20

 proposalTxs := defaultRes . Txs 

 21

 if injection != nil { 

 22

 proposalTxs = append ([][] byte { injection }, proposalTxs ...) 

 23

 h . logger . Debug ( "injected local last commit" , "height" , req . Height ) 

 24

 } 

 25

 return & abcitypes . ResponsePrepareProposal { 

 26

 Txs : proposalTxs , 

 27

 }, nil 

 28

 } 

 29

 } 

```

```

 ctx.ConsensusParams().Abci.VoteExtensionsEnableHeight && collectSigs { //Fails to verify vote extensions with VerifyVoteExtension rules err := baseapp.ValidateVoteExtensions(ctx, h.stakingKeeper, req.Height, ctx.ChainID(), req.LocalLastCommit) if err != nil { return nil, err } injection, err = json.Marshal(req.LocalLastCommit) if err != nil { h.logger.Error("failed to marshal extended votes", "err", err) return nil, err } ... } defaultRes, err := h.defaultPrepareProposal(ctx, req) ... proposalTxs := defaultRes.Txs if injection != nil { proposalTxs = append([][]byte{injection}, proposalTxs...) h.logger.Debug("injected local last commit", "height", req.Height) } return &abcitypes.ResponsePrepareProposal{ Txs: proposalTxs, }, nil }}"> 

 Aside from the more complex variant, pure validation mismatches are also still prevalent despite being a well-known attack surface. This stems from 
```
Proposal
```
 (
```
Vote
```
) rejections by various obscure checks hidden within CometBFT. For example, this commit fixes a bug where PrepareProposal may return a Proposal larger than MaxTxBytes , which will later get rejected by CometBFT.

## The Keymaker 

 States (persistent storage) are another crucial component in state machines. Cosmos relies on a custom key-value store called 
```
KVStore
```
 to handle states efficiently. In 
```
KVStore
```
, keys and values are both represented as simple byte slices, requiring developers to handle serialization and deserialization of more intricate structures when working with storage.

 The complexity behind proper data serialization often results in flawed code and security vulnerabilities. Below, we showcase relatively simple (but buggy) implementations and progressively address and mitigate the issues until the code is deemed safe from exploits.

 Letâs start by considering a scenario where we need to store the 
```
 PositionMap 
```
 structure mentioned below into storage:

```

```
 1

 type VaultId uint64 

 2

 type Username string 

 3

 type PositionName string 

 4

 type Position struct { 

 5

 data [] byte 

 6

 } 

 7

 type PositionMap := 

 8

 map [ VaultId ] map [ Username ] map [ PositionName ] Position 

```

```

 Given that there are three levels of keys in 
```
 PositionMap 
```
, we should try to serialize these three map keys into a hierarchically searchable storage key. The most straightforward approach is to convert all fields into strings and concatenate them together:

```

```
 1

 storageKey := fmt . Sprintf ( 

 2

 " %d%s%s " , 

 3

 vaultId , 

 4

 username , 

 5

 positionName , 

 6

 ) 

```

```

 Although plain concatenation allows us to easily construct a storage key, it becomes apparent that this implementation is prone to key collisions:

```

```
 vaultId = 1, username = "2a", positionName = "b" 

 => storageKey = "12ab" 

 vaultId = 12, username = "a", positionName = "b" 

 => storageKey = "12ab" 

```

```

 storageKey = "12ab"vaultId = 12, username = "a", positionName = "b" => storageKey = "12ab""> 

 So, how can we mitigate this issue? Perhaps we can add a field separator between each field, which would resemble the following:

```

```
 1

 const ( 

 2

 Seperator = "|" 

 3

 ) 

 4

 5

 storageKey := fmt . Sprintf ( 

 6

 " %d%s%s%s%s " , 

 7

 vaultId , 

 8

 Seperator , 

 9

 username , 

 10

 Seperator , 

 11

 positionName , 

 12

 ) 

```

```

 Inserting a separator helps prevent most accidental collisions, but does it completely solve the problem?

 Sadly, it doesnât. Since the 
```
username
```
 and 
```
positionName
```
 are both strings that may contain arbitrary characters (including the separator), collisions can still happen:

```

```
 vaultId = 1, username = "a|", positionName = "b" 

 => storageKey = "1|a||b" 

 vaultId = 1, username = "a", positionName = "|b" 

 => storageKey = "1|a||b" 

```

```

 storageKey = "1|a||b"vaultId = 1, username = "a", positionName = "|b" => storageKey = "1|a||b""> 

 To further mitigate this, we could encode all fields to ensure that the separator is excluded in individual fields, thus making field injections impossible:

```

```
 1

 const ( 

 2

 Seperator = "|" 

 3

 ) 

 4

 5

 usernameEncoded := make ( 

 6

 [] byte , 

 7

 hex . EncodedLen ( len ( username )), 

 8

 ) 

 9

 hex . Encode ( usernameEncoded , username ) 

 10

 11

 positionNameEncoded := make ( 

 12

 [] byte , 

 13

 hex . EncodedLen ( len ( positionName )), 

 14

 ) 

 15

 hex . Encode ( positionNameEncoded , positionName ) 

 16

 17

 storageKey := fmt . Sprintf ( 

 18

 " %d%s%s%s%s " , 

 19

 vaultId , 

 20

 Seperator , 

 21

 usernameEncoded , 

 22

 Seperator , 

 23

 positionNameEncoded 

 24

 ) 

```

```

 We did it. We finally eliminated all potential 
```
 storageKey 
```
 collisions.

 Until now, our focus has primarily been on storing a single structure. We recognize that in real-world applications, we frequently encounter scenarios where multiple structures must be stored as persistent states.

 In the Cosmos framework, it is common for each 
```
Module
```
 to own a few 
```
KVStore
```
s and have individual 
```
Keeper
```
s managing access to storage. Itâs also important to note that each 
```
KVStore
```
 should be independent from one another, alleviating developers from having to worry about key collisions between different 
```
Modules
```
.

 With that being said, what if we have to maintain more than one structure within the same 
```
KVStore
```
?

 To demonstrate this scenario, we introduce the 
```
 AddressMap 
```
 structure, which will be stored in the same 
```
KVStore
```
 we previously used:

```

```
 1

 type VaultId uint64 

 2

 type Username string 

 3

 4

 type PositionName string 

 5

 type Position struct { 

 6

 data [] byte 

 7

 } 

 8

 type PositionMap := 

 9

 map [ VaultId ] map [ Username ] map [ PositionName ] Position 

 10

 11

 type AddressName string 

 12

 type Address struct { 

 13

 data [] byte 

 14

 } 

 15

 type AddressMap := 

 16

 map [ VaultId ] map [ Username ] map [ AddressName ] Address 

```

```

 Referencing previous examples, it is necessary to sanitize/encode each key field and add separators between fields to prevent key collisions. By putting these measures into practice, we present the following implementation:

```

```
 1

 const ( 

 2

 Seperator = "|" 

 3

 ) 

 4

 5

 6

 func PositionMapKey ( 

 7

 vaultId uint64 , 

 8

 username , positionName [] byte , 

 9

 ) ( key [] byte ) { 

 10

 usernameEncoded := make ( 

 11

 [] byte , 

 12

 hex . EncodedLen ( len ( username )), 

 13

 ) 

 14

 hex . Encode ( usernameEncoded , username ) 

 15

 16

 positionNameEncoded := make ( 

 17

 [] byte , 

 18

 hex . EncodedLen ( len ( positionName )), 

 19

 ) 

 20

 hex . Encode ( positionNameEncoded , positionName ) 

 21

 22

 key := fmt . Sprintf ( 

 23

 " %d%s%s%s%s " , 

 24

 vaultId , 

 25

 Seperator , 

 26

 usernameEncoded , 

 27

 Seperator , 

 28

 positionNameEncoded , 

 29

 ) 

 30

 } 

 31

 32

 33

 func AddressMapKey ( 

 34

 vaultId uint64 , 

 35

 username , addressName [] byte 

 36

 ) ( key [] byte ) { 

 37

 usernameEncoded := make ( 

 38

 [] byte , 

 39

 hex . EncodedLen ( len ( username )), 

 40

 ) 

 41

 hex . Encode ( usernameEncoded , username ) 

 42

 43

 addressNameEncoded := make ( 

 44

 [] byte , 

 45

 hex . EncodedLen ( len ( addressName )), 

 46

 ) 

 47

 hex . Encode ( addressNameEncoded , addressName ) 

 48

 49

 key := fmt . Sprintf ( 

 50

 " %d%s%s%s%s " , 

 51

 vaultId , 

 52

 Seperator , 

 53

 usernameEncoded , 

 54

 Seperator , 

 55

 addressNameEncoded , 

 56

 ) 

 57

 } 

```

```

 Unfortunately, when dealing with more than one storage entry within the same 
```
KVStore
```
, the previous implementation is not enough to guarantee key uniqueness. While it still effectively prevents key collisions within each individual structure, it does not prevent cross-structure key collisions:

```

```
 vaultId = 1, username = "a", positionName = "b" 

 => PositionMapKey = "1|a|b" 

 vaultId = 1, username = "a", addressName = "b" 

 => AddressMapKey = "1|a|b" 

```

```

 PositionMapKey = "1|a|b"vaultId = 1, username = "a", addressName = "b" => AddressMapKey = "1|a|b""> 

 To prevent this, add a structure-specific prefix to the start of each key to act as a domain separator:

```

```
 1

 const ( 

 2

 Seperator = "|" 

 3

 PositionMapPrefix = " \x01 " 

 4

 AddressMapPrefix = " \x02 " 

 5

 ) 

 6

 7

 8

 func PositionMapKey ( 

 9

 vaultId uint64 , 

 10

 username , positionName [] byte , 

 11

 ) ( key [] byte ) { 

 12

 usernameEncoded := make ( 

 13

 [] byte , 

 14

 hex . EncodedLen ( len ( username )), 

 15

 ) 

 16

 hex . Encode ( usernameEncoded , username ) 

 17

 18

 positionNameEncoded := make ( 

 19

 [] byte , 

 20

 hex . EncodedLen ( len ( positionName )), 

 21

 ) 

 22

 hex . Encode ( positionNameEncoded , positionName ) 

 23

 24

 key := fmt . Sprintf ( 

 25

 " %s%d%s%s%s%s " , 

 26

 PositionMapPrefix , 

 27

 vaultId , 

 28

 Seperator , 

 29

 usernameEncoded , 

 30

 Seperator , 

 31

 positionNameEncoded , 

 32

 ) 

 33

 } 

 34

 35

 36

 func AddressMapKey ( 

 37

 vaultId uint64 , 

 38

 username , addressName [] byte , 

 39

 ) ( key [] byte ) { 

 40

 usernameEncoded := make ( 

 41

 [] byte , 

 42

 hex . EncodedLen ( len ( username )), 

 43

 ) 

 44

 hex . Encode ( usernameEncoded , username ) 

 45

 46

 addressNameEncoded := make ( 

 47

 [] byte , 

 48

 hex . EncodedLen ( len ( addressName )), 

 49

 ) 

 50

 hex . Encode ( addressNameEncoded , addressName ) 

 51

 52

 key := fmt . Sprintf ( 

 53

 " %s%d%s%s%s%s " , 

 54

 AddressMapPrefix , 

 55

 vaultId , 

 56

 Seperator , 

 57

 usernameEncoded , 

 58

 Seperator , 

 59

 addressNameEncoded , 

 60

 ) 

 61

 } 

```

```

 We now have a proper example of how to serialize storage keys.

 Nonetheless, there is more to storage than just this. As previously mentioned, storage is expected to support its original functionalities. In the case of 
```
 map 
```
, data should still be retrievable through original keys.

 Letâs look at a case where we want to retrieve all 
```
 map [ Username ] map [ PositionName ] Position 
```
 associated with a 
```
 VaultId 
```
 from the storage. How can we safely accomplish this?

 Fortunately, the Cosmos SDK provides APIs to fetch all entries associated with a 
```
 storageKey 
```
 prefix. Below is an example of an attempt to fetch data with 
```
 vaultId 
```
:

```

```
 1

 func FetchPositionMapWithVaultId ( 

 2

 vaultId uint64 , 

 3

 ) ([] map [ Username ] map [ PositionName ] Position ) { 

 4

 values := map [ Username ] map [ PositionName ] Position {} 

 5

 i := sdk . KVStorePrefixIterator ( 

 6

 kvStore , 

 7

 fmt . Sprintf ( " %s%d " , PositionMapPrefix , vaultId ) 

 8

 ) 

 9

 for ; i . Valid (); i . Next () { 

 10

 k := strings . split ( i . Key (), Seperator ) 

 11

 12

 username := make ([] byte , hex . DecodedLen ( k [ 0 ])) 

 13

 _ , err := hex . Decode ( username , k [ 0 ]) 

 14

 if err != nil { 

 15

 return nil , err 

 16

 } 

 17

 18

 positionName := make ([] byte , hex . DecodedLen ( k [ 1 ])) 

 19

 _ , err := hex . Decode ( positionName , k [ 1 ]) 

 20

 if err != nil { 

 21

 return nil , err 

 22

 } 

 23

 24

 if entry , ok := values [ username ]; ! ok { 

 25

 values [ username ] = make ( map [ PositionName ]) 

 26

 } 

 27

 28

 values [ username ][ positionName ] = Position { 

 29

 data : iterator . Value (), 

 30

 } 

 31

 } 

 32

 return values 

 33

 } 

```

```

 By now, you may have already noticed that this implementation suffers from field malleability issues. Imagine a scenario where both 
```
 vaultId = 1 
```
 and 
```
 vaultId = 10 
```
 coexist. If we try to fetch data under 
```
 vaultId = 1 
```
, all entries under 
```
 vaultId = 10 
```
 will also be returned simply because 
```
1
```
 is a prefix of 
```
10
```
. To fix this, we must once again append the 
```
 Seperator 
```
 to the iterator prefix:

```

```
 i := sdk . KVStorePrefixIterator ( 

 kvStore , 

 fmt . Sprintf ( " %s%d%s " , PositionMapPrefix , vaultId , Seperator ), 

 ) 

```

```

 At first, identifying these serialization issues may seem easy. Once data structures and 
```
KVStore
```
 usage grow increasingly complex, developers can unintentionally overlook storage key parsing mistakes.

 Storage keys continue to be a tedious and persistent issue when building on Cosmos. It is crucial to approach development with awareness and care to prevent bugs from creeping into code.

## Real-world examples 

 The Cosmos SDK previously lacked protection against 
```
KVStore
```
 key collisions . This prior oversight allowed developers to unintentionally create two 
```
KVStore
```
s that were not independent of each other ( permalink ):

 store.go 
```

```
 1

 func NewKVStoreKeys ( names ... string ) map [ string ]* KVStoreKey { 

 2

 keys := make ( map [ string ]* KVStoreKey ) 

 3

 for _ , name := range names { 

 4

 keys [ name ] = NewKVStoreKey ( name ) 

 5

 } 

 6

 7

 return keys 

 8

 } 

```

```

 Thanks to the diligence of core developers, checks are now enforced and the Cosmos SDK will refuse to run if any 
```
KVStore
```
 keys are prefixes of each other. This implementation alleviates developers from having to worry about key collisions on the 
```
KVStore
```
 level.

 Additional storage key issues like subtle bugs in the Cosmos SDK have resulted in incorrect iterator behavior .

 Tip Gradual adoption of the collections storage helpers since Cosmos v0.50 has made it a lot more difficult to write buggy code. This demonstrates the importance of keeping up to date with the latest SDK development to leverage architectural security improvements.

## Conclusion 

 The Cosmos SDK is a powerful tool for those who want to create custom blockchains. However, this flexibility brings about great responsibility. Developers must pay close attention to nuances, as these can expose a large number of potential attack surfaces.

 To recap, we discussed some of the more basic parts of the Cosmos SDK, showcasing common mistakes developers tend to make. Yet, it is important to note that weâve only covered the tip of the iceberg. Other attack surfaces, such as authentication in relation to the IBC interface, are fundamentals absolutely worth looking into.
