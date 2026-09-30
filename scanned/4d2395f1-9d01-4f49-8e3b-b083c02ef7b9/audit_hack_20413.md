# [H] OtterSec: Compiler bug causes compiler bug: how a 12-year-old g++ bug took down Solidity

## Summary
Severity: High
Published: Mon, 11 Aug 2025
Source: https://osec.io/blog/compiler-bug-causes-compiler-bug/
Type: security-research

## Details
## Compiler bug causes compiler bug: how a 12-year-old g++ bug took down Solidity

 Kiprey Aug 11, 2025 #solidity #compiler A subtle G++ bug from 2012, C++20âs new comparison rules, and legacy Boost code can collide to crash Solidityâs compiler on valid code. We unpack the surprising chain reaction and how to fix it.

## Introduction 

 Compilers arenât supposed to crash â especially not when compiling perfectly valid code like this:

```

```
 1

 // SPDX-License-Identifier: UNLICENSED 

 2

 pragma solidity ^0.8.25 ; 

 3

 4

 contract A { 

 5

 function a () public pure returns ( uint256 ) { 

 6

 return 1 ** 2 ; 

 7

 } 

 8

 } 

```

```

 Yet running Solidityâs compiler (solc) on this file on a standard Ubuntu 22.04 system (G++ 11.4, Boost 1.74) causes an immediate segmentation fault.

 At first, this seemed absurd. The code just returns 1 to the power of 2 â no memory tricks, unsafe casting, or undefined behavior.

 And yet, it crashes.

 Another minimal example:

```

```
 1

 // SPDX-License-Identifier: UNLICENSED 

 2

 pragma solidity ^0.8.25 ; 

 3

 4

 contract A { 

 5

 function a () public pure { 

 6

 uint256 [ 1 ] data ; 

 7

 } 

 8

 } 

```

```

 Still crashes.

 So whatâs going on?

 We traced it down to a seemingly unrelated C++ line deep in the compiler backend:

```

```
 if (* lengthValue == 0 ) { ... } 

```

```

 That single comparison â a 
```
 boost :: rational 
```
 compared to 0 â causes infinite recursion in G++ < 14 when compiled under C++20. And the resulting stack overflow crashes solc.

 This post unpacks how this happened â and why none of the individual components are technically âbrokenâ:

- A 12-year-old overload resolution bug in G++

- An outdated symmetric comparison pattern in Boost

- A subtle but impactful rewrite rule in C++20

 Put together, they form a perfect storm â one that takes down Solidity compilation on default Linux setups, even though your code is perfectly fine.

## Background: the setup 

 If you follow the Solidity build documentation (v0.8.30) , youâll see it recommends:

- Boost â¥ 1.67

- GCC â¥ 11

 Ubuntu 22.04, for example, ships with:

- G++ 11.4.0

- Boost 1.74.0

 So far, so good.

 However, Solidity enabled C++20 in January 2025 .

 This wasnât accompanied by an update to the versions of dependencies in the documentation. As weâll soon see, thatâs what opened the trapdoor.

## Part I: a 12-year-old G++ bug in overload resolution 

## Whatâs overload resolution? 

 In C++, when you write an expression like 
```
 a == b 
```
, the compiler chooses among available 
```
 operator == 
```
 implementations by comparing their match quality . A member function like 
```
 a . operator ==( b ) 
```
 usually has higher priority than a non-member function like 
```
 operator == ( a , b ) 
```
 â unless the types differ too much or are ambiguous.

 Thatâs the rule. But G++ didnât always follow it.

## The bug 

 In 2012, a bug was filed: GCC Bug 53499 â overload resolution favors non-member function . The issue? In expressions where:

- A class 
```
 rational < T > 
```
 has a templated 
```
 operator == 
```
 member function

- Thereâs also a more generic free 
```
 operator == ( rational < T >, U ) 
```
 function

 Clang correctly chooses the member function. 

 G++ (before v14) chooses the non-member function. 

 Why? Because G++ mishandles templated conversion + non-exact match , overvaluing a non-member function with worse match quality. It does not correctly apply the overload resolution ranking rules defined in CWG532: Member/nonmember operator template partial ordering .

## A minimal reproducer 

 Letâs see this in action:

 main.cpp 
```

```
 1

 # include <iostream> 

 2

 3

 template < typename IntType > 

 4

 class rational { 

 5

 public : 

 6

 template < class T > 

 7

 bool operator == ( const T & i ) const { 

 8

 std :: cout << "clang++ resolved member" << std :: endl ; 

 9

 return true ; 

 10

 } 

 11

 }; 

 12

 13

 template < class Arg , class IntType > 

 14

 bool operator == ( const rational < IntType > & a , const Arg & b ) { 

 15

 std :: cout << "g++ <14 resolved non-member" << std :: endl ; 

 16

 return false ; 

 17

 } 

 18

 19

 int main () { 

 20

 rational < int > r ; 

 21

 return r == 0 ; 

 22

 } 

```

```

 template class rational {public: template  bool operator==(const T& i) const { std::cout bool operator==(const rational & a, const Arg& b) { std::cout r; return r == 0;}"> 

- 
 Compile with g++ < 14:

 Terminal window 
```

```
 g++ -std=c++17 main.cpp -o test && ./test 

```

```

 Output (on g++ 11.4):

```

```
 g++ <14 resolved non-member 

```

```

- 
 Compile with clang++:

 Terminal window 
```

```
 clang++ -std=c++17 main.cpp -o test && ./test 

```

```

 Output:

```

```
 clang++ resolved member 

```

```

 In short, the wrong function gets picked. G++ was broken here until v14.

## Part II: C++20âs symmetric comparison feature 

## What changed in C++20? 

 C++20 introduced the spaceship operator 
```
 <=> 
```
 and defaulted comparison rewrites .

 When you define a two-argument 
```
 operator == 
```
, C++20 may implicitly define the âreversedâ version:

- If you define: 
```
 bool operator == ( T1 , T2 ); 
```

- Then 
```
 T2 == T1 
```
 may call the same function by reversing the arguments.

 This rewrite is recursive : 
```
 a == b 
```
 becomes 
```
 b == a 
```
, which becomes 
```
 a == b 
```
 again, and so on â if not handled carefully.

 This is great for reducing boilerplate â unless the call becomes ambiguous or self-referential.

## Part III: the Boost trapdoor 

 The old Boost 
```
 rational 
```
 class (prior to v1.75) defined both a member function and a non-member function for 
```
 operator == 
```
:

 boost/rational.hpp 
```

```
 1

 template < typename IntType > 

 2

 class rational 

 3

 { 

 4

 ... 

 5

 public : 

 6

 ... 

 7

 8

 template < class T > 

 9

 BOOST_CONSTEXPR typename boost :: enable_if_c < rational_detail :: is_compatible_integer < T , IntType >:: value , bool >:: type operator == ( const T & i ) const 

 10

 { 

 11

 return (( den == IntType ( 1 )) && ( num == i )); 

 12

 } 

 13

 ... 

 14

 } 

 15

 16

 template < class Arg , class IntType > 

 17

 BOOST_CONSTEXPR 

 18

 inline typename boost :: enable_if_c < 

 19

 rational_detail :: is_compatible_integer < Arg , IntType >:: value , bool > ::type 

 20

 operator == ( const Arg & b , const rational < IntType > & a ) 

 21

 { 

 22

 return a == b ; 

 23

 } 

```

```

 class rational{ ...public: ... template  BOOST_CONSTEXPR typename boost::enable_if_c ::value, bool>::type operator== (const T& i) const { return ((den == IntType(1)) && (num == i)); } ...}template BOOST_CONSTEXPRinline typename boost::enable_if_c ::value, bool>::type operator == (const Arg& b, const rational & a){ return a == b;}"> 

 This was designed under C++17 semantics. Back then, 
```
 rhs == lhs 
```
 would fall back to member overloads if available. All good.

 But under C++20 with G++ < 14:

- G++ incorrectly chooses this non-member operator first.

- C++20 reverses the comparison.

- This calls the same function again with the arguments flipped.

- And so onâ¦

 This creates infinite recursion .

 A minimal example:

 main.cpp 
```

```
 1

 // g++ -std=c++20 -o crash main.cpp && ./crash 

 2

 # include <boost/rational.hpp> 

 3

 4

 int main () { 

 5

 boost :: rational < int > r ; 

 6

 return r == 0 ; 

 7

 } 

```

```

 int main() { boost::rational r; return r == 0;}"> 

 Expected output: nothing.

 Actual: segmentation fault (stack overflow).

 This exact pattern was reported and fixed in Boost rational , but only in version 1.75+.

 Hereâs the one-line fix:

 boost/rational.hpp 
```

```
 1

 template < class Arg , class IntType > 

 2

 BOOST_CONSTEXPR 

 3

 inline typename boost :: enable_if_c < 

 4

 rational_detail :: is_compatible_integer < Arg , IntType >:: value , bool > ::type 

 5

 operator == ( const Arg & b , const rational < IntType > & a ) 

 6

 { 

 7

 return a == b ; 

 8

 return a . operator ==( b ); 

 9

 } 

```

```

 BOOST_CONSTEXPRinline typename boost::enable_if_c ::value, bool>::type operator == (const Arg& b, const rational & a){ return a == b; return a.operator==(b);}"> 

 Instead of calling 
```
 a == b 
```
 â which triggers overload resolution again â the patched version directly calls the member function 
```
 operator == 
```
.

 This prevents C++20 from triggering recursive rewrites.

## Part IV: how this breaks Solidity 

 The Solidity codebase uses 
```
 boost :: rational 
```
 to represent certain compile-time constant expressions.

 One snippet that can trigger this issue appears in 
```
 DeclarationTypeChecker :: endVisit () 
```
:

 DeclarationTypeChecker.cpp 
```

```
 1

 if ( Expression const * length = _typeName . length ()) { 

 2

 std :: optional < rational > lengthValue ; 

 3

 4

 if ( length -> annotation (). type && length -> annotation (). type -> category () == Type :: Category :: RationalNumber ) 

 5

 ... 

 6

 else if ( std :: optional < ConstantEvaluator :: TypedRational > value = ConstantEvaluator :: evaluate ( ... )) 

 7

 lengthValue = value -> value ; 

 8

 9

 if (! lengthValue ) 

 10

 ... 

 11

 else if (* lengthValue == 0 ) // <-- Infinite recursion happens here 

 12

 ... 

 13

 } 

```

```

 lengthValue; if (length->annotation().type && length->annotation().type->category() == Type::Category::RationalNumber) ... else if (std::optional value = ConstantEvaluator::evaluate(...)) lengthValue = value->value; if (!lengthValue) ... else if (*lengthValue == 0) // 

 Under normal circumstances, this expression is benign. But:

- G++ < 14 wrongly prefers Boostâs non-member operator.

- C++20 reverses the arguments.

- The non-member operator recursively calls itself.

 ð¥: segmentation fault.

## Part V: what environments are affected? 

 If a system uses any of the following:

- G++ < 14 (e.g., Ubuntu 22.04 uses 11.4)

- Boost < 1.75 (e.g., 1.74 ships with Ubuntu)

- C++20 enabled (default in recent Solidity builds)

 it will encounter this crash as soon as it processes a Solidity source with a length expression like 
```
 T [ 0 ] 
```
 or anything involving compile-time rational comparisons.

## Recommendations 

- Update Boost to â¥ 1.75 

- Pin G++ to v14 or later 

## Conclusion 

 Note This isnât a security vulnerability. It doesnât corrupt memory or allow code execution.

 But it is a reminder of the fragility of modern build stacks. A bug introduced in 2012, fixed in 2024, quietly broke one of the most used blockchain compiler toolchains â all without any code in the Solidity repo being âwrong.â

 Every layer here â Boost, G++, the C++20 spec, and Solidity â behaved âas documented.â But together, they composed into undefined behavior.

 The lesson? Always test critical software under multiple compilers and library versions â especially when enabling a new language standard.
