# [C] RCE on Steam Client via buffer overflow in Server Info

## Summary
Severity: Critical (CVSS 9.6)
Program: Valve
Weakness: Classic Buffer Overflow
Reporter: vinnievan
State: resolved
Disclosed: 2019-03-15T19:47:43.463Z
Source: https://hackerone.com/reports/470520

## Details
## Introduction

In Steam and other valve games (CSGO, Half-Life, TF2) there is a functionality to find game servers called the server browser. In order to retrieve the information about these servers the server browser communicates with a specific UDP protocol called [server queries](https://developer.valvesoftware.com/wiki/Server_queries). The protocol is well described in the online developers manual of Steam. We implemented a custom python server which only replies with the protocol using the same information available in the documentation. After a successful implementation of the protocol we fuzzed several parameters and noticed that the Steam client crashed when receiving replies from our custom server. More specifically, the client crashed when we replied with a large player name used in the `A2S_PLAYER` response. When attaching a debugger we noticed it crashed due to a stack-based buffer overflow.

This clearly indicates that something was wrong and we investigated it further to be able to exploit the buffer overflow. After further inspection, we noticed that the overflow occurred in the `serverbrowser` library. At some point the players’ name is converted into unicode and an overflow occurs because the boundaries are not checked. Also, there’s no canary protection present, which allowed us to overwrite the return address and execute arbitrary code on Windows.

## Exploit details

We wanted to prove impact and build an exploit. First, we tested it on Linux and we were able to control the execution flow instantly by overwriting the return address. However, on Linux, we were able to control two bytes of the `EIP` register only (e.g. `0x00004141`) and we didn’t explore it further. On OSX, the process terminated with `SIGABRT`, which means that there’s probably a canary protection in the library on OSX. Then, we tried to exploit it on Windows and we were successful (tested on Windows 8.1 and 10).

On Windows, sending a player name via UDP like `A*1100` would result in the following stack layout:
```
0x00410041
0x00410041
...
```

This happens due to unicode conversion (wide-char), because player names can use unicode characters. Sending a player name with unicode characters like `u"\u4141"*1100` would result in the following layout:
```
0x41414141
0x41414141
...
```

However, since we were corrupting the stack and registers before the function returns, we had no control over the `EIP` register yet. The program was crashing after dereferencing the `edi` register, but we had control over it. We satisfied these special conditions using constant values present on the `Steam.exe` binary:

{F395516}

Then, we built a unicode ROP chain with gadgets from `Steam.exe` only, to call `VirtualProtect` dynamically to make the stack executable and jump to our unicode shellcode to execute `cmd.exe`. This was a big challenge since we couldn't use values like `0x00000040` in our ROP chain, otherwise the string would be terminated. And we couldn't use invalid unicode characters like `u"\uda01"` because the library replaces them with a question mark `?` - `0x003F`.

**Note:** Everything is calculated using the `Steam.exe` base address. This address changes if you restart your Windows 8 or Windows 10, not if you relaunch Steam. The exploit is 100% reliable if you edit the base address on the exploit, but you can't predict the base address in the computer of a victim due to ASLR. However, we have two exploitation scenarios:

- Only 9 bits are randomized: An attacker can successfully exploit a victim with a probability of 0.2% (1/512), which is more than enough if we are talking about an attacker distributing this exploit massively to all Steam users (1 new victim every 512 attempts in average)
- This vulnerability can be chained with another memory leak vulnerability to make it 100% reliable

## Steps to reproduce

First, make sure that you have Steam installed. If you are using the beta version, please uncomment the beta version gadgets in the exploit code.

_Trimmed to 38 lines — full report: https://hackerone.com/reports/470520_
