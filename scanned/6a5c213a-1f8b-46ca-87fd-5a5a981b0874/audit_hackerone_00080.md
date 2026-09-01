# [M] [Hubs] - Broken access control in placing objects in hubs room

## Summary
Severity: Medium
Program: Mozilla
Weakness: Improper Access Control - Generic
Reporter: quikke
State: resolved
Disclosed: 2023-07-20T12:33:49.622Z
Source: https://hackerone.com/reports/1987011

## Details
Dear team,

First of all, thank you for all the support you already have provided. I hope the migration to HackerOne is not too hard and wish you all of the best!

This was orginally submitted on the bug bounty service of Mozilla itself: https://bugzilla.mozilla.org/show_bug.cgi?id=1829735

## Summary:
In the settings of a hub, an admin user can disable the creation  an object or move deny to move any object. I found out that this is bypassable with the usage of certain `/<commands>` inside the chat feature. An attacker does not to be authenticated nor have joined the room to perform this attack. With some JavaScript magic, we can trick the browser thinking we are in the room, which we are not.

## Requirements:
* Two different browsers - for two accounts
 * Browser A : Admin that creates a room
* Browser B: Attacker

## Setup
You can skip the setup, if you want and make use of my instance: https://quikke.dev.myhubs.net/eE97EwL/quikke-test-server
1. In Browser A, go to https://hello.dev.myhubs.net/
2. Sign in & Create a room
3. Join the room
4. Click on the three dots in the right corner (More)
5. Room info and settings and click on edit (top right)
6. Disable the below listed settings:
   * Create and move objects
   * Pin objects

{F2351238}
7.Click on Apply

## Steps To Reproduce:
In Browser B, go to the room created by the attacker or you can use mine: https://quikke.dev.myhubs.net/eE97EwL/quikke-test-server . Join the meeting and noticed that only the Chat option is available. Open the chat and follow the below steps to create different objects with different settings:

###Add command -  spawn object
= Spawn a duck into the hub as a none admin. Users will still have the ability to open a menu to delete the duck
  1. Enter the following in the chat `/add https://quikke.assets.dev.myhubs.net/hubs/assets/models/DuckyMesh-b80f0ece1f58a683839a..glb`

{F2351241}

###Add command -  spawn object with--no-menu flag

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1987011_
