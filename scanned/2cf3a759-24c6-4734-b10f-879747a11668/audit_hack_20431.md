# [H] Neodyme: Riverguard: How to Get Access to Findings for Your Contract

## Summary
Severity: High
Published: Tue, 23 Jul 2024
Source: https://neodyme.io/en/blog/riverguard-onboarding/
Type: security-research

## Details
Jul 23, 2024 ~11 min read 

## Riverguard: How to Get Access to Findings for Your Contract 

Authored by: - Tobias 

 Welcome to the second blog post in our series on Riverguard, our automated Solana smart contract vulnerability discovery tool. From our first post , you may already know what Riverguard is and how it works:

- Riverguard automatically tests for exploitable bugs in ALL programs currently deployed on Solana Mainnet — open source or not

- It does this by using transactions interacting with a smart contract as template for basic “fuzzing”

- The “fuzzing” consists of mutating and locally re-executing the transactions in ways that uncover common vulnerabilities

- Riverguard has already uncovered numerous loss-of-funds bugs worth millions of dollars

 Don’t worry, though; we don’t exploit the vulnerabilities Riverguard finds. Instead, we store them and make them available to the contract’s developers — you. This post should help you through the registration and verification needed to gain access to all the potential vulnerabilities we’ve found in any smart contracts you’ve deployed on Solana.

## Introduction ¶ 

 Since Breakpoint 2023, we have been scanning all transactions interacting with smart contracts on Solana Mainnet. We developed a powerful tool that detects common vulnerabilities in smart contracts by simulating and mutating previously executed transactions. Accordingly, we have now identified potential security vulnerabilities in deployed contracts. Piles of them. However, for most of them, we only know the public key of the affected smart contracts, not how to contact the developers.

 Here’s where you come in. If you register your smart contracts with Riverguard, you get access to all findings relating to your contract and can triage and fix them yourself. Additionally, we’re manually reviewing a lot of the findings ourselves. By registering and providing contact information, you’ll allow us to reach out to you regarding any potential findings we notice in your contracts and collaborate with you for triaging. This service is free , and no setup is required on your part. It is maintained by Neodyme, with support from the Solana Foundation.

## Registration Process ¶ 

 The registration process is very straightforward and can be completed in only a few minutes. By simply visiting riverguard.io and scrolling down a bit, you will be presented with the registration form:

 Image 1: Riverguard registration form

 Generally, the most critical information for us is your contact details and all public keys of the smart contracts you manage. You can include multiple public keys in the “Program Addresses” field by separating them with new lines (Shift+Enter) or commas. Otherwise, all additional information is optional and could help us triage your findings without any support from your side, including if your code is open source or you have good documentation of your smart contract’s functionality.

 The checkbox “Do you want direct access to findings for your program?” will, after successful verification, allow you to view all existing findings relating to your smart contracts, should any be available. If you leave this box unchecked, we will only store the contact information to reach out to you in case we cannot triage a finding ourselves.

## Verification ¶ 

 After registration, the findings are generally not directly accessible, as anybody could pose as the developer of certain smart contracts. Thus, we must first verify the information provided to enable access and share information about potential security vulnerabilities with the registered user.

 Programs can be deployed and managed in numerous ways, so no one-size-fits-all solution for verification exists. However, the easiest way to verify the authenticity of your provided contact details is probably the presence of a security.txt file in your smart contract(s) with the matching contact email. If this is the case, you should quickly get access after registering with Riverguard. If you don’t have a security.txt yet, please consider adding it. That way, we and everyone else can verify who should get security-related information about your programs.

 If you do not have security.txt and do not wish to add one, you can also verify your ownership by signing a message with your program upgrade authority. If your program is governed by a DAO, you may have to verify through a proposal.

 In general, we accept the following as proof:

- a signed on-chain memo-transaction,

- a signed off-chain message, or

- a successful DAO proposal with your program governance containing a message.

 Examples for generating the first two can be seen below. In either case, the message should contain the following string and data:

```
riverguardauth: <program address>, <email address>
```

 In case of a DAO governance controlling your upgrade authority, we need proof that the DAO approves you being the security contact for the program — either through a security.txt, or via a successful proposal that clearly states that you should have access to riverguard’s findings for the protocol.

 Feel free to suggest some alternative means of verification via verify@riverguard.io if none of the above is feasible for you, and we’ll get back to you as soon as we can.

## On-Chain Memo Message Example ¶ 

 An example of such a memo message can be seen in this transaction :

 Image 2: An on-chain memo transaction, as displayed by the Solana explorer

 To perform such a memo, you can directly use the Solana CLI. For example:

 - 
```

```
 $ solana transfer <pubkey of your fee payer> 1 --fee-payer <KEYPAIR> --from <pubkey of your fee payer> --signer <pubkey of your program upgrade authority> --with-memo "riverguardauth: <pubkey of your smart contract> <your contact email>" 

```

```

## Off-Chain Message Signing Example ¶ 

 You can create a signed off-chain message via the Solana CLI. This will use your upgrade authority’s key to sign the string you provide. We can verify the signature using the public key. (As a side note, be careful: Don’t sign arbitrary messages other people ask you to sign using this authority! Especially if the message content is too general or you don’t understand it.).

 Here’s how to generate such a signature:

```

```
 $ solana sign-offchain-message --keypair <program upgrade authority KEYPAIR> "riverguardauth: <pubkey of your smart contract> <your contact email>" 

```

```

 In our case, this would look as follows:

```

```
 $ solana sign-offchain-message "riverguardauth: Neodyme111111111111111111111111111111111111 contact@neodyme.io" 

```

```

 For us, the resulting output signature is: 
```
iyiqrcCr43PS6N1pzye3NGdV9owGs4C4PNB5inZzK7yA8tMou8nudL8WxJFTu2hqBAhi2QCTcWyk2duZjLjXURc
```

 Afterward, you can send us an email with the message and signature to verify@riverguard.io . Here’s a template with all the information we need:

```

```
 Dear Neodyme-Team, 

 Here is an off-chain message signed by our program upgrade authority: 

 Message: "riverguardauth: Neodyme111111111111111111111111111111111111 contact@neodyme.io" 

 Signature: iyiqrcCr43PS6N1pzye3NGdV9owGs4C4PNB5inZzK7yA8tMou8nudL8WxJFTu2hqBAhi2QCTcWyk2duZjLjXURc 

 Best, 

 Neodyme 

```

```

## Personal Riverguard Dashboard ¶ 

 Once your registration and verification are completed, we will create a Riverguard account for you and send an invitation link to the provided contact email. From there, you will be able to set a password (please choose a strong one) and log in to 
```
riverguard.io
```
.

 Image 3: Invitation message you will receive after registration is complete

 After your login, you will probably see this screen:

 Image 3: What you’ll see when your account was created, but your programs are not yet associated with your account.

 This means that we haven’t assigned any programs to your account yet. Only after our manual verification will we enable access to all the potential findings relating to your smart contract, assuming if you selected this in the registration form.

 Once your account is enabled, you may see a screen like this:

 Image 4: What you’ll see if there are no findings for your contract(s)

 In that case, congratulations! Riverguard has not found any potential vulnerabilities in your programs yet.

 Alternatively, if you have some findings for your contracts, it will look like this:

 Image 5: Some findings were identified relating to your contract

 This is an overview of all findings for your programs, along with which of our mutation rules created them. This gives you some idea of the types of bugs that your program may contain. You will also see a list with all findings and additional details for each in the findings tab, which looks like this:

 Image 6: A list of potential vulnerabilities identified in your contract (in this case, only a single one).

 You can see all available information about the potential vulnerability by clicking on the eye symbol. This includes the date of first discovery, affected program, and fuzzcase that identified the potential vulnerability. You can also set a status and add notes for the findings or the program.

## False Positives ¶ 

 Not all findings listed in the findings table are actual vulnerabilities. Some are false positives. While we strive to detect false positives in our simulation engine, due to the generality of the attacks, it’s impossible to prevent them completely. Thus, we rely on developers like you to review findings, understand the potential vulnerability, and verify it. If you’re fairly certain that the finding is a non-issue, you can mark it as a false positive. However, please be cautious when doing so, as this also means that we will likely ignore them during our manual reviews. That being said, if you fully understand the potential vulnerability and determine that it to be a non-issue, then definitely feel free to mark it. The latter also helps us reduce our workload.

 If you have any questions or problems understanding the vulnerability or finding the related section in your code, feel free to ask us for support at any time via contact@riverguard.io .

## Finding Status ¶ 

 Apart from the 
```
New
```
 flag, which all findings receive when they are initially identified, and the false positive flag, we use other flags to mark the findings. To be precise, the options are as follows:

 Image 7: The possible statuses of a findings. For findings relating to your program, you can set these yourself.

 Most of them are largely self-explanatory. If a finding is in the 
```
In Review
```
 state, somebody on our team is currently investigating this finding and trying to determine whether this is a vulnerability. If the finding is in the 
```
Finished
```
 state, we should have already contacted you, as this bug is already fixed and shouldn’t be detected by Riverguard anymore. The 
```
False Positive
```
 state marks findings as intended features. Thus, a Riverguard fuzzcase will always mark this type of functionality as potentially vulnerable, but it is already triaged, so nobody has to worry about it anymore. The 
```
Awaiting Fix
```
 state marks this finding as a vulnerability already communicated to the developers and denotes that mitigation is being developed. Thus, this finding has also already been triaged and will (hopefully) be resolved soon. Lastly, the most critical state is 
```
Needs Dev Contact
```
. This means that we think there is a good chance this is a real vulnerability, and we had, up until now, no way of contacting the developers. If you have a finding marked as such in your findings table, please contact us as soon as possible via contact@riverguard.io .

## Program Settings ¶ 

 You will also have access to the program settings page after successfully logging in and having programs assigned to your account. Here, we have two customizable settings.

 First, a name can be assigned to the public key of a program, which improves the visibility at a glance of the program affected in the findings table. Second, the deduplication type can be selected for each program. This feature is essential for recognizing identical findings across multiple transactions.

 Image 8: The deduplication option is used to manage how Riverguard attempts to merge findings.

 The problem here boils down to not knowing which portion of the instruction data is responsible for selecting the instruction to be executed and which part serves as an argument for the selected instruction. Therefore, we must guess the instruction signature in the passed instruction data.

 This is relatively easy for anchor programs, as the first 8 bytes always indicate the instruction. However, it is not as trivial for non-anchor programs, as different implementations are not easily detectable. Accordingly, if you have numerous findings likely stemming from the same function in your code, try to change this setting and see if the findings get merged and the deduplication does its job.

## Summary ¶ 

 We hope this introduction to Riverguard will help you navigate our new software to make the Solana ecosystem more secure. We are keen on eliminating all relevant findings generated by Riverguard, which should mitigate the most common and straightforward vulnerabilities in all deployed and utilized smart contracts. For this project, we partnered with the Solana Foundation to offer this service free of charge.

 If you haven’t done it yet, you can now register for your Riverguard account on riverguard.io .

 Riveguard is one of our largest projects to date. However, while Riverguard is powerful, it cannot replace a comprehensive security audit. Its capabilities are limited to common problems that can be detected on-chain and depend on the volume of transactions associated with your smart contract. If your contract hasn’t seen significant traffic, Riverguard may not be able to detect potential issues.

 We hope Riverguard will make your smart contracts more secure, as it is an excellent first layer of protection. Nonetheless, if you are looking for a more in-depth security audit, we are here to assist you. Having found the largest number of loss-of-funds bugs both in Solana itself and in Solana smart contracts, we believe we host the best auditors on Solana. Contact us via contact@neodyme.io to set up an audit, or to talk smart contract security.

 On this page

 - Introduction 

- Registration Process 

- Verification 

 - On-Chain Memo Message Example 

- Off-Chain Message Signing Example 

- Personal Riverguard Dashboard 

 - False Positives 

- Finding Status 

- Program Settings 

- Summary 

 - Solana 

- Riverguard 

 Share:
