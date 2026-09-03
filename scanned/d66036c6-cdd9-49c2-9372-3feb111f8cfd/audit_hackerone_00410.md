# [H] Malformed .MDL triggers an Access Violation on GoldSRC (hl.exe)

## Summary
Severity: High
Program: Valve
Weakness: Memory Corruption - Generic
Reporter: chippy
State: resolved
Disclosed: 2019-10-09T00:01:06.274Z
Source: https://hackerone.com/reports/495793

## Details
A malformed player .MDL triggers an exploitable Access Violation on GoldSRC engine games (Half-Life) upon invocation, which could lead to remote code execution on a client.

###Crash Information
FAILURE_ID_HASH_STRING:  um:invalid_pointer_write_exploitable_c0000005_hw.dll!createinterface
Event Type: Exception
Exception Faulting Address: 0x4c01000
First Chance Exception Type: STATUS_ACCESS_VIOLATION (0xC0000005)
Exception Sub-Type: Write Access Violation

FOLLOWUP_IP: 
hw!CreateInterface+282aa
03a554ea d95efc          fstp    dword ptr [esi-4]

PROBLEM_CLASSES: 

    ID:     [0n309]
    Type:   [@ACCESS_VIOLATION]
    Class:  Addendum
    Scope:  BUCKET_ID
    Name:   Omit
    Data:   Omit
    PID:    [Unspecified]
    TID:    [0x6e30]
    Frame:  [0] : hw!CreateInterface

    ID:     [0n282]
    Type:   [INVALID_POINTER_WRITE]
    Class:  Primary
    Scope:  DEFAULT_BUCKET_ID (Failure Bucket ID prefix)
            BUCKET_ID
    Name:   Add
    Data:   Omit
    PID:    [Unspecified]
    TID:    [0x6e30]
    Frame:  [0] : hw!CreateInterface

    ID:     [0n156]
    Type:   [ZEROED_STACK]

_Trimmed to 38 lines — full report: https://hackerone.com/reports/495793_
