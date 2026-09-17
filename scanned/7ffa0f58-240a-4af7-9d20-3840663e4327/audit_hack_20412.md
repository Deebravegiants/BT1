# [M] OtterSec: PoRv2: a fast, transparent ZK-based proof of reserves

## Summary
Severity: Medium
Published: Wed, 27 Aug 2025
Source: https://osec.io/blog/how-proof-of-reserves-uses-zk-to-protect-your-funds/
Type: security-research

## Details
## PoRv2: a fast, transparent ZK-based proof of reserves

 Caue Obici Aug 27, 2025 #zk #por Here, we explore zk-proofs, Merkle trees, and our new open-source implementation, PoRv2. Our proof of reserves enables users to verify exchange liabilities without relying on external auditors, setting a new standard for trust.

## What is a proof of reserves? 

 At its heart, Proof of Reserves (PoR) is a crucial system designed to show that a crypto platform genuinely holds the funds it owes to its users. Itâs how exchanges and custodians can prove, using strong cryptographic methods, that they have enough assets to cover all customer deposits.

 Think of it this way: PoR is about enabling transparency. Itâs a way for platforms to provide clear, verifiable evidence of their financial health. For users, it means gaining confidence that their funds are secure on the platforms they use.

 Historically, traditional ways of proving reserves often had drawbacks. They might reveal too much sensitive information about the platform and rely heavily on external auditors without a direct user verification method.

 We at OtterSec, in partnership with Backpack , just developed a Proof of Reserves system that can be used to prove CEX solvency. Our Zero-Knowledge Proof of Reserves (PoRv2) was based on the OKX Proof of Reserves algorithm since it was the fastest and most efficient one known so far. We also use recursive plonky2 as the algorithm for zero-knowledge proving, but we made some improvements to the circuits for more transparency and verifiable information on the user side, eliminating the need to trust the audit company.

 In addition, we created and open-sourced a PoR verifier server that receives the proofs and validates them.

## Why do we use ZK for PoR? 

 Proving reserves is crucial, but it presents a unique challenge for any platform holding user funds: how do you publicly prove solvency without also exposing sensitive user balance information or revealing proprietary financial details? This is where Zero-Knowledge Proofs (ZKPs) become game-changers.

 Simply put, a Zero-Knowledge Proof allows one party to prove to another that a statement is true without revealing any information beyond the validity of the statement itself. Imagine proving you know a secret password without actually telling anyone the password. You confirm you possess the knowledge, but the secret remains yours.

 In the context of Proof of Reserves, ZKPs are perfectly suited to solve the privacy paradox. They enable a platform to prove two important things cryptographically:

- Sum proof : The exchange liability is equal to the sum of all usersâ balances (e.g., 
```
 btc_liability = user1_btc + user2_btc + user3_btc + ... 
```
).

- Non-negativity : All users have a positive net balance. This ensures that the sum proof is not tampered with by users with negative net balances. A user can have negative asset balances (e.g., borrowing BTC) but only if collateralized with other assets.

 It is worth noting that we cannot guarantee that all users were included in the ZK analysis. Therefore, if we only used ZKPs to prove those two statements, the exchange could tamper with the sum proof by excluding users from the PoR. Thatâs why we also use a Merkle tree to prove inclusions.

## What is a Merkle tree and how does it help in a PoR? 

 A Merkle tree is a tree data structure where each leaf node is a cryptographic hash of an individual piece of data (like a userâs balance), and every non-leaf node is a cryptographic hash of its child nodes. This structure allows for the entire dataset to be summarized by a single, unique hash at the top, called the Merkle root:

 In the PoR, we can use a Merkle tree to verify the inclusion of each user in the Proof of Reserves. It works like this:

- The Merkle tree is generated using the leaf nodes as the hashes of the user information (e.g., 
```
 sha256 ( { id : 1 , balances : { "BTC" : 0.1 , "ETH" : 0.2 , ...}} ) 
```
).

- The Merkle tree is made public.

- Each user can download the Merkle tree and check if their account was included by hashing their account information and checking if the hash is one of the leaves.

 In other words, this use of the Merkle tree allows users to easily verify that their individual balance was included in the overall total.

## OtterSec PoRv2 

 We just open-sourced our Proof of Reserves code (PoRv2) , which uses the plonky2 ZK algorithm to create a Merkle tree and a final ZK proof that recursively verifies smaller sum and non-negativity proofs.

 We named it PoRv2 because we already had a version based on Vitalikâs proof of solvency , which was not optimal.

## Non-negativity proof 

 In our non-negativity proof, the circuit receives the asset balances of each user and the price of each asset. With these inputs, it calculates the accountâs USD balance and checks if it is greater than 0.

 We also check for overflows during summation to prevent tampering in the final result.

## Sum proof 

 The sum proof verifies a public circuit input that was calculated by summing up all user balances of each asset (e.g., 
```
BTC final: user1_btc + user2_btc ...
```
). Note that each assetâs final sum is not USD-based; we calculate the final balance using the asset balance itself.

## What are the OtterSec PoRv2 key points? 

- Transparency : It is possible for the exchange to safely disclose the entire Merkle tree so users can verify it without the need for an external auditing company. Also, the code allows asset price commitments and verifications.

- Time-efficiency : We were able to reduce the amount of time to prove by more than 100 times from our previous version by generating proofs for 750,000 users within 8 minutes using a Mac M3 Pro. Check our benchmark .

- Memory-efficiency : We were also able to reduce the amount of RAM needed to prove the liabilities of millions of users. Now, we are able to use machines with 16GB.

- Small proofs : We were able to reduce the final proof to less than 500KB and each inclusion proof to ~52KB . The only big file that we need to store is the Merkle tree, which doesnât consume more than 200MB if the PoR parameters are finely adjusted. Additionally, instead of storing each inclusion proof in a static file, we provide an efficient method to generate inclusion proofs on demand, eliminating the need for the exchange to store millions of files and conserving disk space and resources.

- Privacy : We use many cryptographic mechanisms to ensure that the user balances and other private information are kept safe and secret.

## ZK circuits 

 We use two different ZK circuits to generate the final proof:

- Batch circuit

- Recursive circuit

 With those two circuits, we can generate the recursive proof tree:

 Note We are using 512 as 
```
 BATCH_SIZE 
```
 and 8 as 
```
 RECURSIVE_SIZE 
```
, which indicate how many children each circuit has. This is easily adjustable in the code, and the optimal configuration will depend on the number of accounts being proved in the PoR.

 Note We add empty proofs as padding to chunks that donât have the correct length.

 Each non-leaf node in this tree is a ZK proof, which is generated using the related circuit; each circuit also generates the Merkle tree hash of each node, which is included in the Merkle tree.

## Leaf nodes 

 The leaf nodes are the hashes of the account information. Each is calculated in this way:

 h = P o s e i d o n ( a s s e t _ b a l a n c e s 0 Â â£ â£ Â a s s e t _ b a l a n c e s 1 Â . . . Â â£ â£ Â S H A 256 ( u s e r _ i d ) Â â£ â£ Â u s e r _ n o n c e ) h = Poseidon(asset\_balances_0\ ||\ asset\_balances_1\ ...\ ||\ SHA256(user\_id)\ ||\ user\_nonce) h = P ose i d o n ( a sse t _ ba l an ce s 0 â Â â£â£ Â a sse t _ ba l an ce s 1 â Â ... Â â£â£ Â S H A 256 ( u ser _ i d ) Â â£â£ Â u ser _ n o n ce ) 

 In other words, all balances are concatenated with the hashed user ID (which can be a 
```
uuid
```
, a username, or an incremental ID) and with a nonce. The nonce is a random number that serves as a security measure against attackers who could brute-force the hash to find out other usersâ balances. Since the Merkle tree is a public proof, we need to be careful against these types of data leaks.

## Batch circuit 

 The batch circuit is the first proven circuit in the PoR algorithm. It receives the accountsâ information (grouped in 512) and generates the ZK proof with the following inputs and constraints:

### Public inputs 

- Asset prices in USD

- Merkle tree hash

- Summed asset balances

### Private inputs 

- User balances

- Merkle tree leaf hashes

### Constraints 

- a c c o u n t _ e q u i t y i = = Î£ Â a c c o u n t _ a s s e t _ b a l a n c e s i [ a s s e t _ n u m ] Ã a s s e t _ p r i c e s [ a s s e t _ n u m ] account\_equity_i == \Sigma\ account\_asset\_balances_i[asset\_num] \times asset\_prices[asset\_num] a cco u n t _ e q u i t y i â == Î£ Â a cco u n t _ a sse t _ ba l an ce s i â [ a sse t _ n u m ] Ã a sse t _ p r i ces [ a sse t _ n u m ] 

- a c c o u n t _ e q u i t y i â¥ 0 account\_equity_i \geq 0 a cco u n t _ e q u i t y i â â¥ 0 (non-negativity) 

- t o t a l _ a s s e t _ b a l a n c e [ a s s e t _ n u m ] = = Î£ Â a c c o u n t _ a s s e t _ b a l a n c e s i [ a s s e t _ n u m ] total\_asset\_balance[asset\_num] == \Sigma\ account\_asset\_balances_i[asset\_num] t o t a l _ a sse t _ ba l an ce [ a sse t _ n u m ] == Î£ Â a cco u n t _ a sse t _ ba l an ce s i â [ a sse t _ n u m ] (sum proof) 

- m e r k l e _ t r e e _ h a s h = = P o s e i d o n ( h a s h 0 , h a s h 1 , Â . . . , h a s h 511 ) merkle\_tree\_hash == Poseidon(hash_0, hash_1,\ ..., hash_{511}) m er k l e _ t r ee _ ha s h == P ose i d o n ( ha s h 0 â , ha s h 1 â , Â ... , ha s h 511 â ) (Merkle tree hash) 

- a c c o u n t _ a s s e t _ b a l a n c e s i [ a s s e t _ n u m ] < M A X _ S A F E _ I N T / 512 account\_asset\_balances_i[asset\_num] < MAX\_SAFE\_INT/512 a cco u n t _ a sse t _ ba l an ce s i â [ a sse t _ n u m ] < M A X _ S A F E _ I N T /512 (overflow check) â the overflow check is made this way for performance (note that 512 is actually the 
```
 BATCH_SIZE 
```
)

 Here is a visual scheme of the inputs of the batch circuit and how user hashes are generated:

## Recursive circuit 

 Recursive circuits get eight subproofs as input, verify if all the asset prices are the same, and calculate the summed balances and Merkle hash. Here are the inputs and constraints:

### Public inputs 

- Summed asset balances

- Asset prices

- Merkle tree hash

### Private inputs 

- 8 subproofs

### Constraints 

- t o t a l _ a s s e t _ b a l a n c e [ a s s e t _ n u m ] = = Î£ Â s u b p r o o f i . p u b l i c _ i n p u t . a s s e t _ b a l a n c e s [ a s s e t _ n u m ] total\_asset\_balance[asset\_num] == \Sigma\ subproof_i.public\_input.asset\_balances[asset\_num] t o t a l _ a sse t _ ba l an ce [ a sse t _ n u m ] == Î£ Â s u b p r oo f i â . p u b l i c _ in p u t . a sse t _ ba l an ces [ a sse t _ n u m ] (sum proof) 

- a s s e t _ p r i c e [ a s s e t _ n u m ] = = s u b p r o o f i . p u b l i c _ i n p u t . a s s e t _ p r i c e s [ 0 ] asset\_price[asset\_num] == subproof_i.public\_input.asset\_prices[0] a sse t _ p r i ce [ a sse t _ n u m ] == s u b p r oo f i â . p u b l i c _ in p u t . a sse t _ p r i ces [ 0 ] 

- a s s e t _ p r i c e [ a s s e t _ n u m ] = = s u b p r o o f i . p u b l i c _ i n p u t . a s s e t _ p r i c e s [ a s s e t _ n u m ] asset\_price[asset\_num] == subproof_i.public\_input.asset\_prices[asset\_num] a sse t _ p r i ce [ a sse t _ n u m ] == s u b p r oo f i â . p u b l i c _ in p u t . a sse t _ p r i ces [ a sse t _ n u m ] (verifies if all asset prices are the same) 

- m e r k l e _ t r e e _ h a s h = = P o s e i d o n ( h a s h 0 , h a s h 1 , . . . , h a s h 31 ) merkle\_tree\_hash == Poseidon(hash_0, hash_1, ..., hash_{31}) m er k l e _ t r ee _ ha s h == P ose i d o n ( ha s h 0 â , ha s h 1 â , ... , ha s h 31 â ) (Merkle tree hash) 

- checks if each sum is overflowing by checking if the sum of two positive numbers results in a negative one (overflow check) 

 Here is a visual scheme of the inputs of the recursive circuit. Note that this tree only has three levels (L1, L2, L3). Depending on the number of users, it may have more recursive levels:

## Global proof and inclusion proofs 

## Proving 

 After proving all batch circuits and all recursive circuits, we have the final proof (which is the ZK proof of the recursive tree root), the entire Merkle tree, and the user nonces. In our code, it is serialized to 
```
merkle_tree.json
```
, 
```
final_proof.json
```
, and 
```
private_nonces.json
```
 files.

 Using the ZK proof and the Merkle tree, we can already prove the sum of the asset balances and their non-negativity; we refer to this as the âglobal proof.â

 For the user inclusion proofs, we get the Merkle tree, the user asset balances, the identification hash, and the nonce to bundle it in one proof file (
```
inclusion_proof_<id>.json
```
). 1 

## Verifying 

### Global proof 

 To verify the global proof, the code deserializes the 
```
merkle_tree.json
```
 and the 
```
final_proof.json
```
 files and performs these checks:

- Validate if the final proof was generated with a valid and trusted circuit.

- Verify the ZK final proof.

- Verify if asset prices are valid. (It doesnât verify if they match the real price; you need to do it manually. It only verifies if decimals are valid.)

- Verify if the Merkle tree root hash is the same as the final proof 
```
merkle_tree_hash
```
 public input. This ensures that the 
```
merkle_tree.json
```
 and 
```
final_proof.json
```
 are linked (they belong to the same global proof).

- Verify the entire Merkle tree by hashing all the nodes again, starting with the batch circuit, since the verifier wonât have the necessary information to hash the leaves again (for privacy). This ensures that the tree was not tampered with.

### Inclusion proof 

 To verify the inclusion proof, the code deserializes the 
```
inclusion_proof_<id>.json
```
 file and also the 
```
final_proof.json
```
. After that, it performs these checks:

- Verify the ZK final proof.

- Verify if the Merkle tree root is the same as in the final proof.

- Recalculate the user-related node leaf hash.

- Verify a partial Merkle tree using the recalculated hash (it doesnât contain all the leaves).

## PoR verifier server 

 To automate the verification process, we created a verifier server that the exchange can submit the proofs to. Once submitted, the proof is validated and added to the database.

 Once the proof is added, any user can enter the website and see its information (see Backpackâs example):

 Here is a breakdown of what the fields represent and why they are required:

- Status : verifies if the proof is valid, ensuring that the information has not been tampered with.

- Proof Timestamp : when the proof was generated by the exchange.

- Verify Timestamp : when the proof was verified by the PoR server.

- Proof File URL : the URL where the proof was downloaded from. Users can download it to verify the proofâs validity themselves.

- Prover Version : the version of PoRv2 used. Using different versions for proving/verifying can result in errors due to ZK circuit discrepancies. Therefore, if you are going to verify the validity of the proof yourself, ensure that you download and use the same prover version as the proof.

- File Hash (SHA256) : since we only store the URL of the proof, it can be maliciously changed after our verification. SHA256 can be used to prove if the file was modified after the verification. If you are going to verify the proof by yourself, check if the downloaded zip file matches the hash shown on the website.

 Also, you can check the exchangeâs liabilities on the website:

 These are the amounts of assets that the exchange should have in their reserves to be solvent on each asset. You can check if they have them by looking at their reserve wallets on the blockchain. You can see Backpackâs wallets at backpack.exchange/reserves and our verifier server for Backpack at backpack-por.osec.io .

## Self-verification 

 You, as a user, can verify both proofs by yourself: the inclusion proof, to verify if you were included in the PoR total liabilities sum, and the global proof, to verify if the commitments provided by the exchange are valid.

## How to verify if I was included? 

 If you are a user and want to do the self-verification of inclusion, you will need to follow these steps:

- Download the PoRv2 executable from our GitHub .

- Download the inclusion and the final proof files from the exchange (
```
inclusion_proof_<id>.json
```
 and 
```
final_proof.json
```
) and put the files in the same directory as the PoRv2 app.

- Open the terminal and execute this: 
```
 ./plonky2_por verify-inclusion 
```
.

 This will verify if the proofs are valid and show your asset balances. You will need to verify manually that the balances are correct. Remember that the proofs are not calculated in real-time; you must verify if the balances were correct at the proof generation date. Here is an example of a valid proof being verified:

```

```
 [!] The following information was used to generate the proof, please manually verify if they are correct: 

 [!] NOTE: This is not real-time information, verify if the information is correct relative to the time of the proof generation 

 [!] NOTE2: Some asset balances was rounded by some decimals, verify if they are close enough to the original balance 

 ====================== 

 Proof generation date: 2025-02-22 19:59:59 UTC 

 Proof generation timestamp (ms): 1740254399944 

 Number of accounted assets: 100 

 -----Asset balances----- 

 ETH: 0 

 BTC: 1.2 

 USDC: 0 

 ... 

 ====================== 

 [!] Verifying global proof (trusting circuit data inside the file)... 

 [+] Global proof is valid! 

 [!] Verifying inclusion proof... 

 [+] Inclusion proof root hash is valid! The user is included in the merkle tree! 

 [+] Successfully verified inclusion proof for file: inclusion_proof_00476816e43cf2efffdabdda7f55c5203bc9e28382c551f83931de02fd364a25.json 

 [+] All inclusion proofs are valid! 

 [+] Finished in 13.731875ms! 

```

```

## How can I verify the global proof? 

 If you want to verify if the global proof is valid, you just need to follow these steps:

- Download the PoRv2 executable from our GitHub .

- Download the 
```
merkle_tree.json
```
 and the 
```
final_proof.json
```
 files and put them in the same directory as the PoRv2 app. You can download those files from our PoR verifier server (download the zip file and unzip it).

- Open the terminal and execute 
```
 ./plonky2_por verify-inclusion 
```
. This might take a while to verify since it needs to deserialize a big file and verify the final proof circuit (which involves rebuilding it).

 This will verify the global proof and print the asset prices to be manually verified. Note that the asset prices shown are not real-time; you must match them to the price on the proof generation date and time:

```

```
 [!] Verifying the proof of reserves... 

 [!] The following information was used to generate the proof, please manually verify if they are correct: 

 [!] NOTE: This is not real-time information, verify if the information is correct relative to the time of the proof generation 

 [!] NOTE2: Asset prices was rounded by some decimals, verify if they are close enough to the original price 

 ====================== 

 Proof generation date: 2025-02-22 19:59:59 UTC 

 Proof generation timestamp (ms): 1740254399944 

 Number of accounted assets: 100 

 -----Asset prices----- 

 BTC: US$ 95000 

 ETH: US$ 2402.48 

 ... 

 ====================== 

```

```

 When verification is completed, and all proofs are valid, the system will print the summed balances of each asset. These are the liabilities of the exchange, which you can use to check if they have reserves to cover them:

```

```
 [!] Rebuilding root circuit... This might take several minutes... 

 [+] Root circuit rebuilt successfully! 

 [!] Verifying final proof... 

 [+] Proof is valid! 

 [!] Verifying asset prices... 

 [+] Asset prices are valid! 

 [!] Verifying asset decimals... 

 [+] Asset decimals are valid! 

 [!] Verifying merkle tree root hash... 

 [+] Merkle tree root hash is valid! 

 [!] Verifying merkle tree... 

 [+] Merkle tree is valid! 

 [!] The following information is the final needed asset reserves, which was validated by the Zero-Knowledge proof 

 [!] NOTE: This is not real-time information, the information is relative to the time of the proof generation 

 [!] NOTE2: We cannot guarantee that all users were included in the proof, but you can check if you were included by verifying the inclusion proof 

 ====================== 

 Proof generation date: 2025-02-22 19:59:59 UTC 

 Proof generation timestamp (ms): 1740254399944 

 Number of accounted assets: 100 

 -----Asset reserves----- 

 BTC: 1.2 

 ETH: 5.4 

 ... 

 ====================== 

 [+] All proofs are valid! 

 [+] Finished in 4.455745214s! 

```

```

## Conclusion 

 In conclusion, Proof of Reserves serves as a crucial mechanism for crypto platforms, enabling them to demonstrate solvency and gain user trust in a transparent manner. By employing zero-knowledge proofs, platforms can achieve this transparency without exposing sensitive user data, effectively proving total liabilities and ensuring non-negativity while preserving privacy. Our system further refines this process, boosting efficiency and eliminating the need for manual verification.

 We are currently working with Backpack to implement this algorithm in production to generate and verify proofs every 24 hours. This marks a significant advancement toward establishing a real-time Proof of Reserves system, particularly given that it offers increased transparency, which is a step forward in reducing the need for external audit companies, as users will be able to verify everything themselves.

 For more information about how Backpack Exchange implements Proof of Reserves in practice, you can read their detailed article: Proof of Reserves at Backpack Exchange: Real Transparency, ZK Verified .

## Footnotes 

- 
 We bundle only a part of the Merkle tree into the inclusion proof file to make the proof smaller. â©
